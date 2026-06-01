"""Tek Gemini çağrısında özet, anahtar kelime, duygu/ton ve hedef kitle üretir."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Sequence

from google import genai
from google.genai import types

from utils.preprocess import build_topic_blocks, clean_text


DEFAULT_COMBINED_MODEL = "gemini-2.5-flash-lite"


class CombinedAnalysisError(Exception):
    """Birleşik analiz sürecinde oluşan kullanıcı dostu hata sınıfı."""


def _client() -> genai.Client:
    """Gemini istemcisini döndürür."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise CombinedAnalysisError("Birleşik analiz için GEMINI_API_KEY tanımlı değil.")
    return genai.Client(api_key=api_key)


def _extract_json(text: str) -> Dict[str, Any]:
    """Model çıktısından JSON nesnesini ayıklar."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise CombinedAnalysisError("Gemini çıktısı beklenen JSON formatında değil.")
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise CombinedAnalysisError("Gemini çıktısı ayrıştırılamadı.") from exc


def _build_prompt(text: str, summary_ratio: float, blocks: Sequence[Dict[str, Any]]) -> str:
    """Birleşik analiz için istem oluşturur."""
    detail_hint = "orta uzunlukta" if summary_ratio <= 0.30 else "biraz daha detaylı"
    block_text = "\n\n".join(
        f"Blok {index + 1}:\n{block['text']}" for index, block in enumerate(blocks)
    )
    return f"""
Aşağıdaki YouTube video transcriptini analiz et. Türkçe cevap ver.

Tek bir JSON nesnesi döndür. Markdown, açıklama veya kod bloğu kullanma.

Kurallar:
- Özet {detail_hint} olsun.
- Anahtar kelimeler kısa ve güçlü terimler olsun.
- Duygu ve ton analizinde net ama kısa ifadeler kullan.
- Hedef kitle için en fazla 3 kitle belirt.
- Sadece transcriptteki bilgilere dayan.

JSON şeması tam olarak şu olsun:
{{
  "summary": {{
    "main_topic": "...",
    "key_points": ["...", "...", "..."],
    "conclusion": "..."
  }},
  "keywords": ["...", "...", "..."],
  "sentiment": {{
    "general_emotion": "...",
    "dominant_tone": "...",
    "positive_points": ["...", "..."],
    "negative_points": ["...", "..."],
    "short_evaluation": "..."
  }},
  "audience": {{
    "primary_audience": "...",
    "secondary_audience": ["...", "..."],
    "level": "...",
    "rationale": "..."
  }}
}}

Transcript Blokları:
{block_text}

Tam Transcript:
{text[:7000]}
""".strip()


def analyze_video_content(
    text: str,
    segments: Sequence[Dict[str, Any]] | None = None,
    summary_ratio: float = 0.28,
    model_name: str = DEFAULT_COMBINED_MODEL,
) -> Dict[str, Any]:
    """Tek Gemini çağrısıyla tüm temel analizleri üretir."""
    cleaned = clean_text(text)
    if not cleaned:
        raise CombinedAnalysisError("Analiz üretilemedi: transcript metni boş.")

    blocks = build_topic_blocks(list(segments or []), target_block_count=3)
    if not blocks:
        blocks = [{"text": cleaned[:2500]}]

    prompt = _build_prompt(cleaned, summary_ratio, blocks)
    try:
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
            raise CombinedAnalysisError(
                "Gemini ücretsiz kota sınırına ulaşıldı. Bugünkü istek hakkı dolmuş olabilir. "
                "Bir süre bekleyip tekrar dene ya da ücretli plana geç."
            ) from exc
        if "503" in message or "UNAVAILABLE" in message or "high demand" in message.lower():
            raise CombinedAnalysisError(
                "Gemini şu anda yoğun. Kısa süre sonra tekrar denersen analiz yeniden çalışacaktır."
            ) from exc
        raise CombinedAnalysisError(f"Birleşik analiz çağrısı başarısız oldu: {exc}") from exc

    text_output = (getattr(response, "text", "") or "").strip()
    if not text_output:
        raise CombinedAnalysisError("Gemini birleşik analiz çıktısı boş geldi.")

    payload = _extract_json(text_output)
    if not isinstance(payload, dict):
        raise CombinedAnalysisError("Birleşik analiz sonucu beklenen yapıda değil.")
    return payload


def format_summary(payload: Dict[str, Any]) -> str:
    """Özet alanını mevcut arayüze uygun metne çevirir."""
    summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
    main_topic = str(summary.get("main_topic", "-")).strip()
    key_points = summary.get("key_points", [])
    if not isinstance(key_points, list):
        key_points = []
    conclusion = str(summary.get("conclusion", "-")).strip()
    points = "\n".join(f"- {point}" for point in key_points if str(point).strip())
    return (
        f"Ana Konu:\n{main_topic}\n\n"
        f"Önemli Noktalar:\n{points or '-'}\n\n"
        f"Sonuç:\n{conclusion}"
    )


def format_sentiment(payload: Dict[str, Any]) -> str:
    """Duygu/ton alanını mevcut arayüze uygun metne çevirir."""
    sentiment = payload.get("sentiment", {}) if isinstance(payload, dict) else {}
    general = str(sentiment.get("general_emotion", "-")).strip()
    tone = str(sentiment.get("dominant_tone", "-")).strip()
    positive_points = sentiment.get("positive_points", [])
    negative_points = sentiment.get("negative_points", [])
    if not isinstance(positive_points, list):
        positive_points = []
    if not isinstance(negative_points, list):
        negative_points = []
    evaluation = str(sentiment.get("short_evaluation", "-")).strip()
    positive_text = "\n".join(f"- {point}" for point in positive_points if str(point).strip())
    negative_text = "\n".join(f"- {point}" for point in negative_points if str(point).strip())
    return (
        f"Genel Duygu:\n{general}\n\n"
        f"Baskın Ton:\n{tone}\n\n"
        f"Olumlu Unsurlar:\n{positive_text or '-'}\n\n"
        f"Olumsuz Unsurlar:\n{negative_text or '-'}\n\n"
        f"Kısa Değerlendirme:\n{evaluation}"
    )


def format_audience(payload: Dict[str, Any]) -> str:
    """Hedef kitle alanını mevcut arayüze uygun metne çevirir."""
    audience = payload.get("audience", {}) if isinstance(payload, dict) else {}
    primary = str(audience.get("primary_audience", "-")).strip()
    secondary = audience.get("secondary_audience", [])
    if not isinstance(secondary, list):
        secondary = []
    level = str(audience.get("level", "-")).strip()
    rationale = str(audience.get("rationale", "-")).strip()
    secondary_text = "\n".join(f"- {item}" for item in secondary if str(item).strip())
    return (
        f"Ana Hedef Kitle:\n{primary}\n\n"
        f"İkincil Hedef Kitle:\n{secondary_text or '-'}\n\n"
        f"Seviye:\n{level}\n\n"
        f"Gerekçe:\n{rationale}"
    )


def extract_keywords_from_payload(payload: Dict[str, Any], top_n: int = 10) -> List[str]:
    """Birleşik analiz çıktısından anahtar kelimeleri döndürür."""
    keywords = payload.get("keywords", []) if isinstance(payload, dict) else []
    if not isinstance(keywords, list):
        return []
    cleaned = [str(item).strip() for item in keywords if str(item).strip()]
    return cleaned[:top_n]
