"""Gemini tabanlı hedef kitle tahmini."""

from __future__ import annotations

import os
from typing import List, Tuple

from google import genai
from google.genai import types

from utils.preprocess import clean_text


DEFAULT_AUDIENCE_MODEL = "gemini-2.5-flash-lite"


class AudienceAnalysisError(Exception):
    """Hedef kitle analizi sırasında oluşan kullanıcı dostu hata sınıfı."""


def analyze_target_audience(text: str, summary_text: str = "") -> str:
    """Transcript ve özetten hedef kitle tahmini üretir."""
    cleaned = clean_text(text)
    if not cleaned:
        raise AudienceAnalysisError("Hedef kitle analizi için transcript metni boş.")

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise AudienceAnalysisError("Hedef kitle analizi için GEMINI_API_KEY tanımlı değil.")

    prompt = f"""
Aşağıdaki video özeti ve transcript bağlamına göre videonun hedef kitlesini Türkçe olarak tahmin et.

Kurallar:
- Çıktıyı tam olarak şu formatta ver.
- En fazla 3 hedef kitle belirt.
- Gerekçeler kısa ama açıklayıcı olsun.

Ana Hedef Kitle:
...

İkincil Hedef Kitle:
- ...
- ...

Seviye:
...

Gerekçe:
...

Örnek hedef kitle türleri:
- genel izleyici
- teknik kullanıcı
- satın alma düşünenler
- öğrenci
- başlangıç seviyesi kullanıcı
- karşılaştırma yapan kullanıcı

Özet:
{summary_text}

Transcript:
{cleaned[:4500]}
""".strip()

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=DEFAULT_AUDIENCE_MODEL,
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
                "Gemini ücretsiz kota sınırına ulaşıldı. Hedef kitle analizi için günlük istek hakkı dolmuş olabilir."
            ) from exc
        if "503" in message or "UNAVAILABLE" in message or "high demand" in message.lower():
            raise AudienceAnalysisError(
                "Gemini şu anda yoğun olduğu için hedef kitle analizi geçici olarak üretilemedi."
            ) from exc
        raise AudienceAnalysisError(f"Hedef kitle analizi başarısız oldu: {exc}") from exc

    text_output = (getattr(response, "text", "") or "").strip()
    if not text_output:
        raise AudienceAnalysisError("Hedef kitle analizi boş çıktı.")
    return text_output


def parse_audience_table(text: str) -> List[Tuple[str, str]]:
    """Hedef kitle analiz metnini tablo satırlarına dönüştürür."""
    rows: List[Tuple[str, str]] = []
    current_key = ""
    current_value: List[str] = []

    def flush() -> None:
        nonlocal current_key, current_value
        if current_key:
            rows.append((current_key, " ".join(part.strip() for part in current_value if part.strip()).strip()))
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
