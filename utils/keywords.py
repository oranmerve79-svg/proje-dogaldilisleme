"""Anahtar kelime çıkarımı: önce Gemini, gerekirse YAKE fallback."""

from __future__ import annotations

import os
import re
from typing import List

import yake
from google import genai
from google.genai import types

from utils.preprocess import clean_text


DEFAULT_KEYWORD_MODEL = "gemini-2.5-flash-lite"
GENERIC_PATTERNS = (
    "bununla beraber",
    "iyi şekilde",
    "çok iyi",
    "peki gerçekten",
    "şehir içinde",
    "gayet iyi",
    "bir şekilde",
    "model y'nin",
    "model y",
)


def _normalize_keyword(keyword: str) -> str:
    """Anahtar kelimeyi kıyaslama için normalize eder."""
    keyword = keyword.strip().lower()
    keyword = re.sub(r"[^\wçğıöşü\s-]", " ", keyword, flags=re.IGNORECASE)
    keyword = re.sub(r"\s+", " ", keyword).strip()
    return keyword


def _is_good_keyword(keyword: str) -> bool:
    """Düşük kaliteli veya anlamsız ifadeleri eler."""
    normalized = _normalize_keyword(keyword)
    if not normalized:
        return False
    if normalized in GENERIC_PATTERNS:
        return False
    if len(normalized) < 3:
        return False
    if len(normalized.split()) > 4:
        return False
    if normalized.isdigit():
        return False
    return True


def _dedupe_keywords(keywords: List[str], top_n: int) -> List[str]:
    """Anahtar kelimeleri normalize ederek tekrarları temizler."""
    unique: List[str] = []
    seen: set[str] = set()

    for keyword in keywords:
        normalized = _normalize_keyword(keyword)
        if normalized in seen or not _is_good_keyword(keyword):
            continue
        seen.add(normalized)
        unique.append(keyword.strip())
        if len(unique) >= top_n:
            break

    return unique


def _gemini_keywords(summary_text: str, transcript_text: str, language: str, top_n: int) -> List[str]:
    """Gemini ile yüksek kaliteli anahtar kelime çıkarmayı dener."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return []

    language_name = "Türkçe" if language == "tr" else "İngilizce"
    prompt = f"""
Aşağıdaki video özeti ve transcript bağlamına göre {top_n} adet güçlü anahtar kelime veya kısa anahtar ifade çıkar.

Kurallar:
- Çıktı dili {language_name} olsun.
- Sadece konuya gerçekten özgü terimler üret.
- "çok iyi", "bununla beraber", "iyi şekilde" gibi genel ifadeleri kullanma.
- Tek kelime veya en fazla 4 kelimelik kısa ifadeler kullan.
- Marka, model, teknik kavram, maliyet, özellik, sorun ve karşılaştırma odaklı terimleri tercih et.
- Sadece anahtar kelimeleri ver, açıklama yazma.
- Her satıra bir anahtar kelime yaz.

Özet:
{summary_text}

Transcript Bağlamı:
{transcript_text[:5000]}
""".strip()

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=DEFAULT_KEYWORD_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )
        text = (getattr(response, "text", "") or "").strip()
        if not text:
            return []
        candidates = [
            line.lstrip("-•0123456789. ").strip()
            for line in text.splitlines()
            if line.strip()
        ]
        return _dedupe_keywords(candidates, top_n)
    except Exception:
        return []


def _yake_keywords(text: str, language: str, top_n: int) -> List[str]:
    """Gemini yoksa YAKE ile fallback anahtar kelime üretir."""
    cleaned = clean_text(text)
    if not cleaned:
        return []

    extractor = yake.KeywordExtractor(
        lan=language,
        n=3,
        dedupLim=0.75,
        top=top_n * 3,
    )
    keywords = [keyword for keyword, _score in extractor.extract_keywords(cleaned)]
    return _dedupe_keywords(keywords, top_n)


def extract_keywords(text: str, summary_text: str = "", language: str = "tr", top_n: int = 8) -> List[str]:
    """Önce Gemini, gerekirse YAKE ile anahtar kelime çıkarır."""
    cleaned = clean_text(text)
    cleaned_summary = clean_text(summary_text)
    if not cleaned and not cleaned_summary:
        return []

    gemini_result = _gemini_keywords(cleaned_summary, cleaned, language, top_n)
    if gemini_result:
        return gemini_result

    fallback_corpus = f"{cleaned_summary}. {cleaned}" if cleaned_summary else cleaned
    return _yake_keywords(fallback_corpus, language, top_n)
