"""Analiz raporlarını PDF çıktısına dönüştürür."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any, Dict

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


REGULAR_FONT_NAME = "ReportArial"
BOLD_FONT_NAME = "ReportArialBold"
REGULAR_FONT_PATHS = [
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
]
BOLD_FONT_PATHS = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Verdana Bold.ttf",
]


def _register_pdf_fonts() -> tuple[str, str]:
    """Türkçe karakterleri destekleyen PDF fontlarını kaydeder."""
    regular_path = next((path for path in REGULAR_FONT_PATHS if Path(path).exists()), None)
    bold_path = next((path for path in BOLD_FONT_PATHS if Path(path).exists()), None)
    if not regular_path:
        return "Helvetica", "Helvetica-Bold"

    if REGULAR_FONT_NAME not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(REGULAR_FONT_NAME, regular_path))

    if bold_path and BOLD_FONT_NAME not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(BOLD_FONT_NAME, bold_path))
        return REGULAR_FONT_NAME, BOLD_FONT_NAME

    return REGULAR_FONT_NAME, REGULAR_FONT_NAME


def build_pdf_report(payload: Dict[str, Any]) -> bytes:
    """Analiz sonucundan PDF çıktısı üretir."""
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    regular_font, bold_font = _register_pdf_fonts()
    for style_name in ["BodyText", "Title", "Heading2"]:
        styles[style_name].fontName = bold_font if style_name in ["Title", "Heading2"] else regular_font
    story = []

    report_lines = [
        ("Title", "YouTube Video Özetleme Raporu"),
        ("Heading2", "Video Bilgileri"),
        ("BodyText", f"Video Linki: {payload.get('video_url', '-')}"),
        ("BodyText", f"Analiz Tarihi: {payload.get('created_at', '-')}"),
        ("BodyText", f"Transcript Kaynağı: {payload.get('transcript_source', '-')}"),
        ("Heading2", "Oluşturulan Özet"),
        ("BodyText", str(payload.get("summary_text", "-"))),
        ("Heading2", "Çevrilmiş Özet"),
        ("BodyText", str(payload.get("translated_summary", "-"))),
        ("Heading2", "Anahtar Kelimeler"),
        ("BodyText", ", ".join(payload.get("keywords", [])) or "-"),
        ("Heading2", "Argo Analizi"),
        ("BodyText", str(payload.get("translated_slang_analysis", "-"))),
        ("Heading2", "Duygu ve Ton Analizi"),
        ("BodyText", str(payload.get("translated_sentiment_analysis", "-"))),
        ("Heading2", "Hedef Kitle Analizi"),
        ("BodyText", str(payload.get("translated_audience_analysis", "-"))),
    ]

    for style_name, text in report_lines:
        story.append(Paragraph(text.replace("\n", "<br/>"), styles[style_name]))
        story.append(Spacer(1, 8))

    document.build(story)
    return buffer.getvalue()
