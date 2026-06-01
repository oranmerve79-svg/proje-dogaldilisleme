"""Dil çevirisi işlemleri: varsayılan Türkçe yapı ve seçilen dile çeviri desteği."""

from __future__ import annotations

from typing import List, Tuple

from deep_translator import GoogleTranslator


DEFAULT_LANGUAGE_CODE = "tr"

LANGUAGE_OPTIONS = {
    "Türkçe": "tr",
    "İngilizce": "en",
    "Almanca": "de",
    "Fransızca": "fr",
    "İspanyolca": "es",
}


def translate_text(text: str, target_language: str = DEFAULT_LANGUAGE_CODE) -> Tuple[str, str]:
    """Metni seçilen dile çevirir. Varsayılan hedef dil Türkçedir."""
    if not text.strip():
        return "", "Çeviri atlandı: transcript metni boş."

    if target_language == DEFAULT_LANGUAGE_CODE:
        return text, "Varsayılan dil Türkçe olduğu için transcript doğrudan gösterildi."

    try:
        translated_text = GoogleTranslator(source="auto", target=target_language).translate(text)
        return translated_text, ""
    except Exception as exc:
        return text, f"Çeviri sırasında hata oluştu. Orijinal transcript gösterildi: {exc}"


def translate_large_text(
    text: str,
    target_language: str,
    source_language: str = "auto",
    chunk_size: int = 3200,
) -> Tuple[str, str]:
    """Uzun metni çeviri servisine daha güvenli parçalar halinde gönderir."""
    if not text.strip():
        return "", "Çeviri atlandı: metin boş."

    if source_language == target_language:
        return text, ""

    chunks: List[str] = []
    current = []
    current_len = 0
    for word in text.split():
        if current and current_len + len(word) + 1 > chunk_size:
            chunks.append(" ".join(current))
            current = [word]
            current_len = len(word)
        else:
            current.append(word)
            current_len += len(word) + 1
    if current:
        chunks.append(" ".join(current))

    translated_chunks: List[str] = []
    try:
        translator = GoogleTranslator(source=source_language, target=target_language)
        for chunk in chunks:
            translated_chunks.append(translator.translate(chunk))
        return " ".join(translated_chunks), ""
    except Exception as exc:
        return text, f"Uzun metin çevirisi sırasında hata oluştu. Orijinal metin korundu: {exc}"
