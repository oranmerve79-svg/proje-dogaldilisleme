"""Yerel kullanıcı, geçmiş analiz ve oturum verisi saklama yardımcıları."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


DB_PATH = Path(__file__).resolve().parents[1] / "app_data.db"


def _connect() -> sqlite3.Connection:
    """SQLite bağlantısı açar."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """Gerekli tabloları oluşturur."""
    connection = _connect()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                video_url TEXT NOT NULL,
                transcript_source TEXT,
                output_language TEXT,
                summary_ratio REAL,
                payload_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_url TEXT NOT NULL,
                transcript_source TEXT,
                output_language TEXT,
                summary_ratio REAL,
                payload_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_analysis_cache_lookup
            ON analysis_cache(video_url, transcript_source, output_language, summary_ratio)
            """
        )
        connection.commit()
    finally:
        connection.close()


def _hash_password(password: str) -> str:
    """Parolayı SHA-256 ile hashler."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_user(username: str, password: str) -> tuple[bool, str]:
    """Yeni kullanıcı oluşturur."""
    username = username.strip()
    if len(username) < 3:
        return False, "Kullanıcı adı en az 3 karakter olmalı."
    if len(password) < 4:
        return False, "Parola en az 4 karakter olmalı."

    connection = _connect()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, _hash_password(password)),
        )
        connection.commit()
        return True, "Kullanıcı oluşturuldu."
    except sqlite3.IntegrityError:
        return False, "Bu kullanıcı adı zaten kayıtlı."
    finally:
        connection.close()


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Kullanıcıyı doğrular."""
    connection = _connect()
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, username FROM users WHERE username = ? AND password_hash = ?",
            (username.strip(), _hash_password(password)),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {"id": int(row["id"]), "username": str(row["username"])}
    finally:
        connection.close()


def save_analysis(
    user_id: int,
    video_url: str,
    transcript_source: str,
    output_language: str,
    summary_ratio: float,
    payload: Dict[str, Any],
) -> int:
    """Analiz sonucunu veritabanına kaydeder."""
    connection = _connect()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO analyses (
                user_id, video_url, transcript_source, output_language, summary_ratio, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                video_url,
                transcript_source,
                output_language,
                summary_ratio,
                json.dumps(payload, ensure_ascii=False),
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)
    finally:
        connection.close()


def get_user_history(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    """Kullanıcının son analiz geçmişini listeler."""
    connection = _connect()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT id, video_url, transcript_source, output_language, created_at
            FROM analyses
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        rows = cursor.fetchall()
        return [
            {
                "id": int(row["id"]),
                "video_url": str(row["video_url"]),
                "transcript_source": str(row["transcript_source"] or ""),
                "output_language": str(row["output_language"] or ""),
                "created_at": str(row["created_at"]),
            }
            for row in rows
        ]
    finally:
        connection.close()


def get_analysis_by_id(analysis_id: int) -> Optional[Dict[str, Any]]:
    """Belirli bir analiz kaydını döndürür."""
    connection = _connect()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT id, user_id, video_url, transcript_source, output_language, summary_ratio, payload_json, created_at
            FROM analyses
            WHERE id = ?
            """,
            (analysis_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        payload = json.loads(str(row["payload_json"]))
        payload.update(
            {
                "id": int(row["id"]),
                "user_id": int(row["user_id"]),
                "video_url": str(row["video_url"]),
                "transcript_source": str(row["transcript_source"] or ""),
                "output_language": str(row["output_language"] or ""),
                "summary_ratio": float(row["summary_ratio"] or 0.0),
                "created_at": str(row["created_at"]),
            }
        )
        return payload
    finally:
        connection.close()


def get_cached_analysis(
    video_url: str,
    transcript_source: str,
    output_language: str,
    summary_ratio: float,
) -> Optional[Dict[str, Any]]:
    """Aynı parametrelerle önceden üretilmiş analiz sonucunu döndürür."""
    connection = _connect()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT payload_json, created_at, updated_at
            FROM analysis_cache
            WHERE video_url = ? AND transcript_source = ? AND output_language = ? AND summary_ratio = ?
            LIMIT 1
            """,
            (video_url, transcript_source, output_language, summary_ratio),
        )
        row = cursor.fetchone()
        if not row:
            return None
        payload = json.loads(str(row["payload_json"]))
        payload["cache_created_at"] = str(row["created_at"])
        payload["cache_updated_at"] = str(row["updated_at"])
        return payload
    finally:
        connection.close()


def upsert_cached_analysis(
    video_url: str,
    transcript_source: str,
    output_language: str,
    summary_ratio: float,
    payload: Dict[str, Any],
) -> None:
    """Analiz sonucunu önbelleğe yazar veya günceller."""
    connection = _connect()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO analysis_cache (
                video_url, transcript_source, output_language, summary_ratio, payload_json
            ) VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(video_url, transcript_source, output_language, summary_ratio)
            DO UPDATE SET
                payload_json = excluded.payload_json,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                video_url,
                transcript_source,
                output_language,
                summary_ratio,
                json.dumps(payload, ensure_ascii=False),
            ),
        )
        connection.commit()
    finally:
        connection.close()
