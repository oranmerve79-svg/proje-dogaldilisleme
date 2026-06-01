"""Gemini tabanlı duygu ve anlatım tonu analizi."""

from __future__ import annotations

import os
from typing import Dict, List, Tuple

from google import genai
from google.genai import types

from utils.preprocess import clean_text


DEFAULT_SENTIMENT_MODEL = "gemini-2.5-flash-lite"


class SentimentAnalysisError(Exception):
    """Duygu analizi sırasında oluşan kullanıcı dostu hata sınıfı."""


def parse_sentiment_table(text: str) -> List[Tuple[str, str]]:
    """Yapılandırılmış duygu analizini tablo satırlarına dönüştürür."""
    rows: List[Tuple[str, str]] = []
    current_key = ""
    current_value: List[str] = []

    def flush() -> None:
        nonlocal current_key, current_value
        if current_key:
            value = " ".join(part.strip() for part in current_value if part.strip()).strip()
            rows.append((current_key, value))
        current_key = ""
        current_value = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.endswith(":") and not line.startswith("-"):
            flush()
            current_key = line[:-1]
            continue
        if line.startswith("-"):
            current_value.append(line.lstrip("- ").strip())
        else:
            current_value.append(line)

    flush()
    return rows


def build_sentiment_visual_data(rows: List[Tuple[str, str]]) -> Dict[str, int]:
    """Duygu analizi satırlarını görselleştirme için yaklaşık skorlara çevirir."""
    row_map = {key.lower(): value.lower() for key, value in rows}

    metrics = {
        "Olumluluk": 50,
        "Olumsuzluk": 50,
        "Eleştirel Ton": 40,
        "Bilgilendiricilik": 60,
        "Heyecan Düzeyi": 35,
    }

    general = row_map.get("genel duygu", "")
    tone = row_map.get("baskın ton", "")
    positives = row_map.get("olumlu unsurlar", "")
    negatives = row_map.get("olumsuz unsurlar", "")
    evaluation = row_map.get("kısa değerlendirme", "")
    combined = " ".join([general, tone, positives, negatives, evaluation])

    if any(word in general for word in ["olumlu", "pozitif"]):
        metrics["Olumluluk"] = 78
        metrics["Olumsuzluk"] = 28
    elif any(word in general for word in ["olumsuz", "negatif"]):
        metrics["Olumluluk"] = 30
        metrics["Olumsuzluk"] = 80
    elif "karışık" in general:
        metrics["Olumluluk"] = 58
        metrics["Olumsuzluk"] = 62
    elif "nötr" in general:
        metrics["Olumluluk"] = 45
        metrics["Olumsuzluk"] = 40

    if any(word in combined for word in ["eleştirel", "eksik", "sorun", "olumsuz", "dezavantaj"]):
        metrics["Eleştirel Ton"] = 82
    if any(word in combined for word in ["bilgilendirici", "teknik", "karşılaştırma", "değerlendirme"]):
        metrics["Bilgilendiricilik"] = 88
    if any(word in combined for word in ["heyecanlı", "çarpıcı", "çok güçlü", "iddialı"]):
        metrics["Heyecan Düzeyi"] = 76
    elif any(word in combined for word in ["nötr", "sakin", "dengeli"]):
        metrics["Heyecan Düzeyi"] = 42

    if positives and negatives:
        positive_count = positives.count("-") + positives.count(",") + 1
        negative_count = negatives.count("-") + negatives.count(",") + 1
        if negative_count > positive_count:
            metrics["Olumsuzluk"] = min(90, metrics["Olumsuzluk"] + 8)
        elif positive_count > negative_count:
            metrics["Olumluluk"] = min(90, metrics["Olumluluk"] + 8)

    return metrics


def analyze_sentiment_and_tone(text: str, summary_text: str = "") -> str:
    """Transcript ve özetten duygu ve ton analizi üretir."""
    cleaned = clean_text(text)
    if not cleaned:
        raise SentimentAnalysisError("Duygu analizi için transcript metni boş.")

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise SentimentAnalysisError("Duygu analizi için GEMINI_API_KEY tanımlı değil.")

    prompt = f"""
Aşağıdaki video özeti ve transcript bağlamına göre Türkçe bir duygu ve ton analizi üret.

Kurallar:
- Çıktı kısa ama açıklayıcı olsun.
- Metnin geneline göre karar ver, sadece tek bir cümleye dayanma.
- İnceleme videosu olabileceğini dikkate al.
- Çıktıyı tam olarak şu formatta ver:

Genel Duygu:
...

Baskın Ton:
...

Olumlu Unsurlar:
- ...
- ...

Olumsuz Unsurlar:
- ...
- ...

Kısa Değerlendirme:
...

Özet:
{summary_text}

Transcript:
{cleaned[:5000]}
""".strip()

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=DEFAULT_SENTIMENT_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )
    except Exception as exc:
        message = str(exc)
        if "RESOURCE_EXHAUSTED" in message or "quota" in message.lower() or "429" in message:
            raise SentimentAnalysisError(
                "Gemini ücretsiz kota sınırına ulaşıldı. Duygu ve ton analizi için günlük istek hakkı dolmuş olabilir."
            ) from exc
        if "503" in message or "UNAVAILABLE" in message or "high demand" in message.lower():
            raise SentimentAnalysisError(
                "Gemini şu anda yoğun olduğu için duygu ve ton analizi geçici olarak üretilemedi."
            ) from exc
        raise SentimentAnalysisError(f"Duygu/ton analizi başarısız oldu: {exc}") from exc

    text_output = (getattr(response, "text", "") or "").strip()
    if not text_output:
        raise SentimentAnalysisError("Duygu/ton analizi boş çıktı.")
    return text_output
