"""Argo ve kaba ifade tespiti için yardımcı fonksiyonlar."""

from __future__ import annotations

import re
from collections import Counter
from typing import List, Tuple

from utils.preprocess import clean_text
SLANG_TERMS = [
    "salak",
    "saçma",
    "aptal",
    "gerizekalı",
    "lan",
    "ulan",
    "bok",
    "boktan",
    "mal",
    "rezalet",
    "berbat",
    "çöp",
    "saçmalık",
    "manyak",
]


def _find_slang_terms(text: str) -> List[str]:
    """Metin içinde sözlük tabanlı argo/kaba ifade taraması yapar."""
    lowered = clean_text(text).lower()
    found: List[str] = []
    for term in SLANG_TERMS:
        pattern = rf"(?<!\w){re.escape(term)}(?!\w)"
        matches = re.findall(pattern, lowered, flags=re.IGNORECASE)
        if matches:
            found.extend([term] * len(matches))
    return found


def _slang_level(count: int, word_count: int) -> str:
    """Argo yoğunluğuna göre seviye döndürür."""
    if count == 0:
        return "Yok"
    density = count / max(word_count, 1)
    if count <= 2 and density < 0.01:
        return "Düşük"
    if count <= 5 and density < 0.025:
        return "Orta"
    return "Yüksek"


def analyze_slang(text: str, summary_text: str = "") -> str:
    """Sözlük tabanlı argo tespiti yapar."""
    cleaned = clean_text(text)
    if not cleaned:
        return "Argo Analizi:\n- İncelenecek metin bulunamadı."

    found_terms = _find_slang_terms(cleaned)
    term_counter = Counter(found_terms)
    count = sum(term_counter.values())
    level = _slang_level(count, len(cleaned.split()))
    found_display = ", ".join(f"{term} ({freq})" for term, freq in term_counter.most_common()) or "Bulunmadı"
    if count == 0:
        comment = "Metinde belirgin argo veya kaba ifade tespit edilmedi."
    elif level == "Düşük":
        comment = "Günlük konuşma diline yakın, sınırlı sayıda kaba veya sert ifade bulundu."
    elif level == "Orta":
        comment = "Metinde dikkat çekici düzeyde argo veya sert günlük ifade kullanımı mevcut."
    else:
        comment = "Metinde yoğun argo veya kaba ifade kullanımı gözlemleniyor."

    lines = [
        "Argo Analizi:",
        f"- Argo/Kaba İfade Durumu: {'Var' if count else 'Yok'}",
        f"- Yoğunluk Seviyesi: {level}",
        f"- Tespit Edilen İfadeler: {found_display}",
        f"- Yorum: {comment}",
    ]
    return "\n".join(lines)


def parse_slang_table(text: str) -> List[Tuple[str, str]]:
    """Argo analiz metnini tablo satırlarına dönüştürür."""
    rows: List[Tuple[str, str]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line == "Argo Analizi:":
            continue
        if line.startswith("-") and ":" in line:
            key, value = line.lstrip("- ").split(":", 1)
            rows.append((key.strip(), value.strip()))
    return rows
