"""Transcript alma işlemleri: önce Whisper, gerekirse YouTube transcript fallback."""

from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import Dict, List
from urllib.parse import parse_qs, urlparse

from faster_whisper import WhisperModel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import CouldNotRetrieveTranscript, NoTranscriptFound
from yt_dlp import YoutubeDL


class TranscriptError(Exception):
    """Transcript işlemleri sırasında oluşan kullanıcı dostu hata sınıfı."""


def extract_video_id(video_url: str) -> str:
    """YouTube linkinden video kimliğini ayıklar."""
    if not video_url:
        raise TranscriptError("Geçersiz YouTube linki: boş değer verildi.")

    parsed_url = urlparse(video_url.strip())

    if parsed_url.netloc in {"youtu.be", "www.youtu.be"}:
        video_id = parsed_url.path.lstrip("/")
    elif "youtube.com" in parsed_url.netloc:
        if parsed_url.path == "/watch":
            video_id = parse_qs(parsed_url.query).get("v", [""])[0]
        elif parsed_url.path.startswith("/shorts/") or parsed_url.path.startswith("/embed/"):
            parts = [part for part in parsed_url.path.split("/") if part]
            video_id = parts[1] if len(parts) > 1 else ""
        else:
            video_id = ""
    else:
        match = re.search(r"([A-Za-z0-9_-]{11})", video_url)
        video_id = match.group(1) if match else ""

    if not video_id:
        raise TranscriptError("Geçersiz YouTube linki: video kimliği bulunamadı.")

    return video_id


def download_audio(video_url: str, output_dir: str) -> Path:
    """Video sesini geçici klasöre indirir."""
    output_template = str(Path(output_dir) / "%(id)s.%(ext)s")
    ydl_options = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "quiet": True,
        "noplaylist": True,
        "nocheckcertificate": True,
    }

    try:
        with YoutubeDL(ydl_options) as ydl:
            info = ydl.extract_info(video_url, download=True)
            downloaded_path = ydl.prepare_filename(info)
    except Exception as exc:
        raise TranscriptError(f"Video sesi indirilemedi: {exc}") from exc

    return Path(downloaded_path)


def transcribe_with_whisper(video_url: str, model_size: str = "small") -> Dict[str, List[Dict] | str]:
    """Whisper ile transcript üretir."""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_path = download_audio(video_url, temp_dir)
            model = WhisperModel(model_size, compute_type="int8")
            segments, _info = model.transcribe(str(audio_path), vad_filter=True)

            transcript_segments: List[Dict] = []
            for segment in segments:
                text = (segment.text or "").strip()
                if not text:
                    continue
                transcript_segments.append(
                    {
                        "start": float(segment.start),
                        "end": float(segment.end),
                        "text": text,
                    }
                )
    except TranscriptError:
        raise
    except Exception as exc:
        raise TranscriptError(f"Whisper transkripsiyonu başarısız oldu: {exc}") from exc

    transcript_text = " ".join(item["text"] for item in transcript_segments).strip()
    if not transcript_text:
        raise TranscriptError("Whisper transcript boş geldi.")

    return {
        "text": transcript_text,
        "segments": transcript_segments,
        "source": "whisper",
    }


def transcribe_with_youtube_api(video_url: str, languages: list[str] | None = None) -> Dict[str, List[Dict] | str]:
    """youtube-transcript-api ile fallback transcript üretir."""
    video_id = extract_video_id(video_url)
    languages = languages or ["tr", "en"]

    try:
        if hasattr(YouTubeTranscriptApi, "get_transcript"):
            transcript_items = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        else:
            transcript_items = YouTubeTranscriptApi().fetch(video_id, languages=languages)
    except NoTranscriptFound as exc:
        raise TranscriptError("Bu video için transcript bulunamadı.") from exc
    except CouldNotRetrieveTranscript as exc:
        raise TranscriptError("Transcript alınamadı. Video erişimi veya transcript ayarlarını kontrol edin.") from exc
    except Exception as exc:
        raise TranscriptError(f"Transcript alınırken hata oluştu: {exc}") from exc

    transcript_segments: List[Dict] = []
    for item in transcript_items:
        if isinstance(item, dict):
            text = item.get("text", "").strip()
            start = float(item.get("start", 0.0))
            duration = float(item.get("duration", 0.0))
            end = start + duration
        else:
            text = getattr(item, "text", "").strip()
            start = 0.0
            end = 0.0
        if not text:
            continue
        transcript_segments.append({"start": start, "end": end, "text": text})

    transcript_text = " ".join(item["text"] for item in transcript_segments).strip()
    if not transcript_text:
        raise TranscriptError("Transcript boş geldi.")

    return {
        "text": transcript_text,
        "segments": transcript_segments,
        "source": "youtube_transcript_api",
    }


def fetch_transcript_payload(
    video_url: str,
    languages: list[str] | None = None,
    mode: str = "auto",
) -> Dict[str, List[Dict] | str]:
    """Transcripti seçilen moda göre alır."""
    if mode == "youtube":
        payload = transcribe_with_youtube_api(video_url, languages=languages)
        payload["warning"] = ""
        return payload

    if mode == "whisper":
        payload = transcribe_with_whisper(video_url)
        payload["warning"] = ""
        return payload

    # auto mode: önce Whisper, sonra fallback
    whisper_error = ""
    try:
        payload = transcribe_with_whisper(video_url)
        payload["warning"] = ""
        return payload
    except TranscriptError as exc:
        whisper_error = str(exc)

    payload = transcribe_with_youtube_api(video_url, languages=languages)
    payload["warning"] = f"Whisper kullanılamadı, YouTube transcript fallback kullanıldı: {whisper_error}"
    return payload


def fetch_transcript_text(video_url: str, languages: list[str] | None = None, mode: str = "auto") -> str:
    """Yalnızca transcript metnini döndürür."""
    return str(fetch_transcript_payload(video_url, languages=languages, mode=mode)["text"])
