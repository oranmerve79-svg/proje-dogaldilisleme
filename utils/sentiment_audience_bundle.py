"""Duygu/ton ve hedef kitleyi tek Gemini çağrısında üretir."""

from __future__ import annotations

import json
import os
import re
from typing import Dict, List

from google import genai
from google.genai import types

from utils.audience import AudienceAnalysisError
from utils.preprocess import clean_text


DEFAULT_INSIGHT_MODEL = "gemini-2.5-flash-lite"


def _client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise AudienceAnalysisError("Duygu ve hedef kitle analizi için GEMINI_API_KEY tanımlı değil.")
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
            raise AudienceAnalysisError("Duygu/hedef kitle çıktısı beklenen JSON formatında değil.")
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise AudienceAnalysisError("Duygu/hedef kitle çıktısı ayrıştırılamadı.") from exc


def _build_prompt(text: str, summary_text: str) -> str:
    return f"""
Aşağıdaki video özeti ve transcript bağlamına göre Türkçe analiz üret.

Sadece tek bir JSON nesnesi döndür. Markdown veya açıklama yazma.

JSON şeması:
{{
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

Kurallar:
- Duygu ve ton analizi kısa ama açıklayıcı olsun.
- Hedef kitle için en fazla 3 kitle belirt.
- Sadece transcript ve özete dayan.

Özet:
{summary_text}

Transcript:
{text[:5000]}
""".strip()


def analyze_sentiment_and_audience(
    text: str,
    summary_text: str,
    model_name: str = DEFAULT_INSIGHT_MODEL,
) -> Dict[str, str]:
    cleaned = clean_text(text)
    if not cleaned:
        raise AudienceAnalysisError("Duygu ve hedef kitle analizi için transcript metni boş.")

    prompt = _build_prompt(cleaned, summary_text)
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
            raise AudienceAnalysisError(
                "Gemini ücretsiz kota sınırına ulaşıldı. Duygu, ton ve hedef kitle için günlük istek hakkı dolmuş olabilir."
            ) from exc
        if "503" in message or "UNAVAILABLE" in message or "high demand" in message.lower():
            raise AudienceAnalysisError(
                "Gemini şu anda yoğun olduğu için duygu, ton ve hedef kitle analizi geçici olarak üretilemedi."
            ) from exc
        raise AudienceAnalysisError(f"Duygu/hedef kitle analizi başarısız oldu: {exc}") from exc

    text_output = (getattr(response, "text", "") or "").strip()
    if not text_output:
        raise AudienceAnalysisError("Duygu/hedef kitle çıktısı boş geldi.")

    payload = _extract_json(text_output)
    sentiment = payload.get("sentiment", {})
    audience = payload.get("audience", {})
    if not isinstance(sentiment, dict) or not isinstance(audience, dict):
        raise AudienceAnalysisError("Duygu/hedef kitle çıktısı beklenen yapıda değil.")

    positive_points = sentiment.get("positive_points", [])
    negative_points = sentiment.get("negative_points", [])
    if not isinstance(positive_points, list):
        positive_points = []
    if not isinstance(negative_points, list):
        negative_points = []

    secondary = audience.get("secondary_audience", [])
    if not isinstance(secondary, list):
        secondary = []

    sentiment_text = (
        f"Genel Duygu:\n{str(sentiment.get('general_emotion', '-')).strip()}\n\n"
        f"Baskın Ton:\n{str(sentiment.get('dominant_tone', '-')).strip()}\n\n"
        "Olumlu Unsurlar:\n"
        + "\n".join(f"- {str(point).strip()}" for point in positive_points if str(point).strip())
        + "\n\nOlumsuz Unsurlar:\n"
        + "\n".join(f"- {str(point).strip()}" for point in negative_points if str(point).strip())
        + f"\n\nKısa Değerlendirme:\n{str(sentiment.get('short_evaluation', '-')).strip()}"
    )

    audience_text = (
        f"Ana Hedef Kitle:\n{str(audience.get('primary_audience', '-')).strip()}\n\n"
        "İkincil Hedef Kitle:\n"
        + "\n".join(f"- {str(item).strip()}" for item in secondary if str(item).strip())
        + f"\n\nSeviye:\n{str(audience.get('level', '-')).strip()}\n\n"
        f"Gerekçe:\n{str(audience.get('rationale', '-')).strip()}"
    )

    return {
        "sentiment_text": sentiment_text,
        "audience_text": audience_text,
    }
