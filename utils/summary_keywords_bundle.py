"""Özet ve anahtar kelimeleri tek Gemini çağrısında üretir."""

from __future__ import annotations

import json
import os
import re
from typing import Dict, List, Sequence

from google import genai
from google.genai import types

from utils.preprocess import build_topic_blocks, clean_text
from utils.summarizer import DEFAULT_SUMMARIZER_MODEL, SummarizationError


def _client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise SummarizationError("Gemini özetleme için GEMINI_API_KEY tanımlı değil.")
    return genai.Client(api_key=api_key)


def _extract_json(text: str) -> Dict[str, object]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise SummarizationError("Özet/anahtar kelime çıktısı beklenen JSON formatında değil.")
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise SummarizationError("Özet/anahtar kelime çıktısı ayrıştırılamadı.") from exc


def _build_prompt(text: str, summary_ratio: float, blocks: Sequence[Dict[str, object]]) -> str:
    detail_hint = "orta uzunlukta" if summary_ratio <= 0.30 else "biraz daha detaylı"
    block_text = "\n\n".join(
        f"Blok {index + 1}:\n{str(block.get('text', '')).strip()}"
        for index, block in enumerate(blocks)
        if str(block.get("text", "")).strip()
    )
    return f"""
Aşağıdaki YouTube video transcriptini analiz et ve Türkçe cevap ver.

Sadece tek bir JSON nesnesi döndür. Markdown veya açıklama yazma.

Kurallar:
- Özet {detail_hint} olsun.
- Çıktı tam olarak şu alanları içersin.
- Anahtar kelimeler kısa, konuya özgü ve güçlü ifadeler olsun.
- Genel ifadeler kullanma.

JSON şeması:
{{
  "summary": {{
    "main_topic": "...",
    "key_points": ["...", "...", "..."],
    "conclusion": "..."
  }},
  "keywords": ["...", "...", "..."]
}}

Transcript Blokları:
{block_text}

Tam Transcript:
{text[:7000]}
""".strip()


def summarize_and_extract_keywords(
    text: str,
    segments: Sequence[Dict[str, object]] | None = None,
    summary_ratio: float = 0.28,
    model_name: str = DEFAULT_SUMMARIZER_MODEL,
    top_n: int = 10,
) -> Dict[str, object]:
    cleaned = clean_text(text)
    if not cleaned:
        raise SummarizationError("Özet üretilemedi: transcript metni boş.")

    blocks = build_topic_blocks(list(segments or []), target_block_count=3)
    if not blocks:
        blocks = [{"text": cleaned[:2500]}]

    prompt = _build_prompt(cleaned, summary_ratio, blocks)
    try:
        try:
            response = _client().models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                ),
            )
        except Exception as retryable_exc:
            if "client has been closed" not in str(retryable_exc).lower():
                raise
            response = _client().models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                ),
            )
    except Exception as exc:
        message = str(exc)
        if "RESOURCE_EXHAUSTED" in message or "quota" in message.lower() or "429" in message:
            raise SummarizationError(
                "Gemini ücretsiz kota sınırına ulaşıldı. Bugünkü istek hakkı dolmuş olabilir. "
                "Bir süre bekleyip tekrar dene ya da ücretli plana geç."
            ) from exc
        if "503" in message or "UNAVAILABLE" in message or "high demand" in message.lower():
            raise SummarizationError(
                "Gemini şu anda yoğun. Kısa süre sonra tekrar denersen özetleme yeniden çalışacaktır."
            ) from exc
        raise SummarizationError(f"Özet/anahtar kelime çağrısı başarısız oldu: {exc}") from exc

    text_output = (getattr(response, "text", "") or "").strip()
    if not text_output:
        raise SummarizationError("Özet/anahtar kelime çıktısı boş geldi.")

    payload = _extract_json(text_output)
    summary = payload.get("summary", {})
    if not isinstance(summary, dict):
        raise SummarizationError("Özet çıktısı beklenen yapıda değil.")
    keywords = payload.get("keywords", [])
    if not isinstance(keywords, list):
        keywords = []

    normalized_keywords = [
        str(keyword).strip()
        for keyword in keywords
        if str(keyword).strip()
    ][:top_n]

    summary_text = (
        f"Ana Konu:\n{str(summary.get('main_topic', '-')).strip()}\n\n"
        f"Önemli Noktalar:\n"
        + "\n".join(
            f"- {str(point).strip()}"
            for point in summary.get("key_points", [])
            if str(point).strip()
        )
        + f"\n\nSonuç:\n{str(summary.get('conclusion', '-')).strip()}"
    )

    return {
        "summary_text": summary_text,
        "keywords": normalized_keywords,
    }
