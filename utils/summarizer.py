"""Gemini API ile LLM tabanlı yapılandırılmış özetleme."""

from __future__ import annotations

import os
from typing import Dict, List, Sequence

from google import genai
from google.genai import types

from utils.preprocess import build_topic_blocks, clean_text


class SummarizationError(Exception):
    """Özetleme sürecinde oluşan kullanıcı dostu hata sınıfı."""


DEFAULT_SUMMARIZER_MODEL = "gemini-2.5-flash-lite"


def _client() -> genai.Client:
    """Gemini istemcisini döndürür."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise SummarizationError("Gemini özetleme için GEMINI_API_KEY tanımlı değil.")
    return genai.Client(api_key=api_key)


def _call_gemini_summary(prompt: str, model_name: str) -> str:
    """Gemini generate_content çağrısı yapar."""
    try:
        client = _client()
        response = client.models.generate_content(
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
        raise SummarizationError(f"Gemini özetleme çağrısı başarısız oldu: {exc}") from exc

    text = getattr(response, "text", "") or ""
    if not text.strip():
        raise SummarizationError("Gemini özetleme çıktısı boş geldi.")
    return text.strip()


def _block_prompt(block_text: str) -> str:
    """Tek bir konu bloğu için ara özet promptu."""
    return f"""
Aşağıdaki transcript parçasını Türkçe olarak özetle.

Kurallar:
- Gereksiz giriş cümlesi yazma.
- Ana fikri ve önemli detayları koru.
- Çok kısa yazma, çok da uzatma.
- 3 ila 5 cümle arasında açıklayıcı bir özet üret.
- Sadece transcriptte geçen bilgilerden yararlan.

Transcript:
{block_text}
""".strip()


def _final_prompt(partial_summaries: Sequence[str], summary_ratio: float) -> str:
    """Ara özetlerden final özet oluşturan prompt."""
    detail_hint = "orta uzunlukta" if summary_ratio <= 0.30 else "biraz daha detaylı"
    joined = "\n\n".join(f"Blok {index + 1} Özeti:\n{text}" for index, text in enumerate(partial_summaries))
    return f"""
Aşağıda aynı videonun farklı bölümlerinden çıkarılmış ara özetler var.
Bunları tek ve düzgün bir Türkçe özet halinde birleştir.

Kurallar:
- Çıktı {detail_hint} olsun.
- Ana konu, önemli noktalar ve sonuç bölümlerini koru.
- Tekrarlayan ifadeleri sil.
- Videonun sadece girişine değil, tamamına dayan.
- Teknik ve anlaşılır yaz.
- Çıktıyı tam olarak şu formatta ver:

Ana Konu:
...

Önemli Noktalar:
- ...
- ...
- ...

Sonuç:
...

Ara özetler:
{joined}
""".strip()


def summarize_text(text: str, segments: Sequence[Dict] | None = None, summary_ratio: float = 0.28, model_name: str = DEFAULT_SUMMARIZER_MODEL) -> str:
    """Transcripti bloklara ayırıp Gemini ile yapılandırılmış özet üretir."""
    cleaned_text = clean_text(text)
    if not cleaned_text:
        raise SummarizationError("Özet üretilemedi: transcript metni boş.")

    blocks = build_topic_blocks(list(segments or []), target_block_count=3)
    if not blocks:
        raise SummarizationError("Özet üretilemedi: konu blokları oluşturulamadı.")

    partial_summaries: List[str] = []
    for block in blocks:
        partial_summaries.append(_call_gemini_summary(_block_prompt(block["text"]), model_name))

    return _call_gemini_summary(_final_prompt(partial_summaries, summary_ratio), model_name)
