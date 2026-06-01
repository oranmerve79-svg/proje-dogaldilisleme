"""Transcript temizleme, cümleleştirme ve blok hazırlama yardımcıları."""

from __future__ import annotations

import re
from typing import Dict, List, Sequence


SPACE_RE = re.compile(r"\s+")
FILLER_RE = re.compile(r"\b(eee|ııı|hmm|şey|yani|abi|arkadaşlar)\b", re.IGNORECASE)
NOISE_RE = re.compile(r"\[[^\]]*\]|\([^\)]*(applause|music|laughter)[^\)]*\)", re.IGNORECASE)
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def clean_text(text: str) -> str:
    """Ham transcript metnini daha okunabilir hale getirir."""
    text = text or ""
    text = NOISE_RE.sub(" ", text)
    text = FILLER_RE.sub(" ", text)
    text = text.replace("\n", " ").strip()
    return SPACE_RE.sub(" ", text)


def normalize_segment_text(text: str) -> str:
    """Segment metnini tek cümle gibi normalize eder."""
    cleaned = clean_text(text)
    if not cleaned:
        return ""
    if cleaned[-1] not in ".!?":
        cleaned += "."
    cleaned = cleaned[0].upper() + cleaned[1:] if len(cleaned) > 1 else cleaned.upper()
    return cleaned


def normalize_segments(segments: Sequence[Dict]) -> List[Dict]:
    """Transcript segmentlerini temizler ve normalize eder."""
    normalized: List[Dict] = []
    for segment in segments:
        text = normalize_segment_text(str(segment.get("text", "")))
        if len(text.split()) < 5:
            continue
        normalized.append(
            {
                "start": float(segment.get("start", 0.0)),
                "end": float(segment.get("end", 0.0)),
                "text": text,
            }
        )
    return normalized


def preview_text(text: str, char_limit: int = 1500) -> str:
    """Arayüzde gösterilecek kısa metin ön izlemesini döndürür."""
    cleaned = clean_text(text)
    if len(cleaned) <= char_limit:
        return cleaned
    return f"{cleaned[:char_limit].rstrip()}..."


def split_sentences(text: str) -> List[str]:
    """Metni cümlelere böler."""
    cleaned = clean_text(text)
    if not cleaned:
        return []
    return [sentence.strip() for sentence in SENTENCE_SPLIT_RE.split(cleaned) if sentence.strip()]


def build_topic_blocks(segments: Sequence[Dict], target_block_count: int = 5) -> List[Dict]:
    """Segmentleri video boyunca dağılmış bloklara ayırır."""
    normalized_segments = normalize_segments(segments)
    if not normalized_segments:
        return []

    segment_count = len(normalized_segments)
    block_size = max(3, segment_count // target_block_count)
    blocks: List[Dict] = []

    for index in range(0, segment_count, block_size):
        block_segments = normalized_segments[index : index + block_size]
        if not block_segments:
            continue
        block_text = " ".join(segment["text"] for segment in block_segments).strip()
        if len(block_text.split()) < 18:
            continue
        blocks.append(
            {
                "start": block_segments[0]["start"],
                "end": block_segments[-1]["end"],
                "text": block_text,
                "segments": block_segments,
            }
        )

    return blocks
