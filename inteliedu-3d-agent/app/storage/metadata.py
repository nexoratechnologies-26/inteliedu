"""Metadata persistence for generation jobs and completed videos (PostgreSQL or SQLite)."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.api.schemas import GenerationRequest, VideoMetadata
from app.config import Settings, get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def compute_request_hash(req: GenerationRequest) -> str:
    """Deterministic cache key for deduplicating identical video requests."""
    normalized = {
        "topic": req.topic.strip().lower(),
        "class": req.class_level,
        "subject": req.subject.strip().lower(),
        "board": req.board.strip().lower(),
        "chapter": (req.chapter or "").strip().lower(),
        "language": req.language.strip().lower(),
        "duration": req.duration,
        "include_narration": req.include_narration,
        "include_subtitles": req.include_subtitles,
    }
    raw = json.dumps(normalized, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


class MetadataRepository:
    """Dual-backend repository using PostgreSQL when DATABASE_URL is set, else SQLite."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self.db_path = self.settings.resolved_generated_dir / "metadata.db"
        self._use_postgres = bool(self.settings.database_url)
        self._init_schema()

    def _connect_sqlite(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _connect_pg(self):
        import psycopg  # type: ignore

        return psycopg.connect(self.settings.database_url)

    def _init_schema(self) -> None:
        if self._use_postgres:
            try:
                with self._connect_pg() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """
                            CREATE TABLE IF NOT EXISTS generation_jobs (
                                job_id TEXT PRIMARY KEY,
                                status TEXT NOT NULL,
                                progress_pct INTEGER NOT NULL DEFAULT 0,
                                current_stage TEXT NOT NULL DEFAULT 'queued',
                                message TEXT NOT NULL DEFAULT '',
                                content_hash TEXT,
                                request_json JSONB NOT NULL,
                                result_json JSONB,
                                created_at TIMESTAMPTZ NOT NULL,
                                updated_at TIMESTAMPTZ NOT NULL
                            );
                            CREATE TABLE IF NOT EXISTS generated_videos (
                                video_id TEXT PRIMARY KEY,
                                job_id TEXT NOT NULL,
                                topic TEXT NOT NULL,
                                title TEXT NOT NULL,
                                class_level INTEGER NOT NULL,
                                subject TEXT NOT NULL,
                                board TEXT NOT NULL,
                                status TEXT NOT NULL,
                                video_url TEXT NOT NULL,
                                thumbnail_url TEXT,
                                subtitle_url TEXT,
                                duration DOUBLE PRECISION NOT NULL,
                                format TEXT NOT NULL,
                                generation_engine TEXT NOT NULL,
                                is_simulated BOOLEAN NOT NULL DEFAULT FALSE,
                                content_hash TEXT NOT NULL,
                                metadata_json JSONB NOT NULL,
                                created_at TIMESTAMPTZ NOT NULL
                            );
                            CREATE INDEX IF NOT EXISTS idx_generated_videos_hash
                                ON generated_videos (content_hash);
                            """
                        )
                    conn.commit()
                return
            except Exception as exc:
                logger.warning("PostgreSQL unavailable (%s); falling back to local SQLite store.", exc)
                self._use_postgres = False

        with self._connect_sqlite() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS generation_jobs (
                    job_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    progress_pct INTEGER NOT NULL DEFAULT 0,
                    current_stage TEXT NOT NULL DEFAULT 'queued',
                    message TEXT NOT NULL DEFAULT '',
                    content_hash TEXT,
                    request_json TEXT NOT NULL,
                    result_json TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS generated_videos (
                    video_id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    title TEXT NOT NULL,
                    class_level INTEGER NOT NULL,
                    subject TEXT NOT NULL,
                    board TEXT NOT NULL,
                    status TEXT NOT NULL,
                    video_url TEXT NOT NULL,
                    thumbnail_url TEXT,
                    subtitle_url TEXT,
                    duration REAL NOT NULL,
                    format TEXT NOT NULL,
                    generation_engine TEXT NOT NULL,
                    is_simulated INTEGER NOT NULL DEFAULT 0,
                    content_hash TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_generated_videos_hash
                    ON generated_videos (content_hash);
                """
            )

    def upsert_job(
        self,
        *,
        job_id: str,
        status: str,
        progress_pct: int,
        current_stage: str,
        message: str,
        request_data: Dict[str, Any],
        result_data: Optional[Dict[str, Any]] = None,
        content_hash: Optional[str] = None,
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        req_str = json.dumps(request_data)
        res_str = json.dumps(result_data) if result_data is not None else None

        if self._use_postgres:
            with self._connect_pg() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO generation_jobs
                            (job_id, status, progress_pct, current_stage, message, content_hash, request_json, result_json, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s)
                        ON CONFLICT (job_id) DO UPDATE SET
                            status = EXCLUDED.status,
                            progress_pct = EXCLUDED.progress_pct,
                            current_stage = EXCLUDED.current_stage,
                            message = EXCLUDED.message,
                            result_json = EXCLUDED.result_json,
                            updated_at = EXCLUDED.updated_at
                        """,
                        (job_id, status, progress_pct, current_stage, message, content_hash, req_str, res_str, now, now),
                    )
                conn.commit()
            return

        with self._connect_sqlite() as conn:
            existing = conn.execute(
                "SELECT created_at FROM generation_jobs WHERE job_id = ?", (job_id,)
            ).fetchone()
            created_at = existing["created_at"] if existing else now
            conn.execute(
                """
                INSERT OR REPLACE INTO generation_jobs
                    (job_id, status, progress_pct, current_stage, message, content_hash, request_json, result_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (job_id, status, progress_pct, current_stage, message, content_hash, req_str, res_str, created_at, now),
            )

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        if self._use_postgres:
            with self._connect_pg() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT job_id, status, progress_pct, current_stage, message, content_hash, request_json, result_json, created_at, updated_at FROM generation_jobs WHERE job_id = %s",
                        (job_id,),
                    )
                    row = cur.fetchone()
            if not row:
                return None
            return {
                "job_id": row[0],
                "status": row[1],
                "progress_pct": row[2],
                "current_stage": row[3],
                "message": row[4],
                "content_hash": row[5],
                "request": row[6],
                "result": row[7] or {},
                "created_at": str(row[8]),
                "updated_at": str(row[9]),
            }

        with self._connect_sqlite() as conn:
            row = conn.execute("SELECT * FROM generation_jobs WHERE job_id = ?", (job_id,)).fetchone()
        if not row:
            return None
        return {
            "job_id": row["job_id"],
            "status": row["status"],
            "progress_pct": row["progress_pct"],
            "current_stage": row["current_stage"],
            "message": row["message"],
            "content_hash": row["content_hash"],
            "request": json.loads(row["request_json"]),
            "result": json.loads(row["result_json"]) if row["result_json"] else {},
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def save_video(self, metadata: VideoMetadata) -> None:
        meta_dict = metadata.model_dump(by_alias=True)
        meta_json = json.dumps(meta_dict)
        if self._use_postgres:
            with self._connect_pg() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO generated_videos
                            (video_id, job_id, topic, title, class_level, subject, board, status, video_url, thumbnail_url, subtitle_url, duration, format, generation_engine, is_simulated, content_hash, metadata_json, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                        ON CONFLICT (video_id) DO UPDATE SET
                            status = EXCLUDED.status,
                            video_url = EXCLUDED.video_url,
                            thumbnail_url = EXCLUDED.thumbnail_url,
                            metadata_json = EXCLUDED.metadata_json
                        """,
                        (
                            metadata.video_id,
                            metadata.job_id,
                            metadata.topic,
                            metadata.title,
                            metadata.class_level,
                            metadata.subject,
                            metadata.board,
                            metadata.status,
                            metadata.video_url,
                            metadata.thumbnail_url,
                            metadata.subtitle_url,
                            metadata.duration,
                            metadata.format,
                            metadata.generation_engine,
                            metadata.is_simulated,
                            metadata.content_hash,
                            meta_json,
                            metadata.created_at,
                        ),
                    )
                conn.commit()
            return

        with self._connect_sqlite() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO generated_videos
                    (video_id, job_id, topic, title, class_level, subject, board, status, video_url, thumbnail_url, subtitle_url, duration, format, generation_engine, is_simulated, content_hash, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    metadata.video_id,
                    metadata.job_id,
                    metadata.topic,
                    metadata.title,
                    metadata.class_level,
                    metadata.subject,
                    metadata.board,
                    metadata.status,
                    metadata.video_url,
                    metadata.thumbnail_url,
                    metadata.subtitle_url,
                    metadata.duration,
                    metadata.format,
                    metadata.generation_engine,
                    1 if metadata.is_simulated else 0,
                    metadata.content_hash,
                    meta_json,
                    metadata.created_at,
                ),
            )

    def get_video(self, video_id: str) -> Optional[Dict[str, Any]]:
        if self._use_postgres:
            with self._connect_pg() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT metadata_json FROM generated_videos WHERE video_id = %s", (video_id,))
                    row = cur.fetchone()
            return row[0] if row else None

        with self._connect_sqlite() as conn:
            row = conn.execute(
                "SELECT metadata_json FROM generated_videos WHERE video_id = ?", (video_id,)
            ).fetchone()
        return json.loads(row["metadata_json"]) if row else None

    def find_cached_video(self, content_hash: str) -> Optional[Dict[str, Any]]:
        if self._use_postgres:
            with self._connect_pg() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT metadata_json FROM generated_videos WHERE content_hash = %s AND status = 'completed' AND is_simulated = FALSE ORDER BY created_at DESC LIMIT 1",
                        (content_hash,),
                    )
                    row = cur.fetchone()
            return row[0] if row else None

        with self._connect_sqlite() as conn:
            row = conn.execute(
                "SELECT metadata_json FROM generated_videos WHERE content_hash = ? AND status = 'completed' AND is_simulated = 0 ORDER BY created_at DESC LIMIT 1",
                (content_hash,),
            ).fetchone()
        if not row:
            return None
        meta = json.loads(row["metadata_json"])
        local_vid = meta.get("local_video_path")
        if local_vid and not Path(local_vid).is_file() and meta.get("storage_provider") == "local":
            return None
        return meta

    def list_videos(
        self,
        topic: Optional[str] = None,
        class_level: Optional[int] = None,
        subject: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        if self._use_postgres:
            clauses = ["1=1"]
            params: List[Any] = []
            if topic:
                clauses.append("LOWER(topic) LIKE %s")
                params.append(f"%{topic.lower()}%")
            if class_level is not None:
                clauses.append("class_level = %s")
                params.append(class_level)
            if subject:
                clauses.append("LOWER(subject) = %s")
                params.append(subject.lower())
            params.append(limit)
            sql = f"SELECT metadata_json FROM generated_videos WHERE {' AND '.join(clauses)} ORDER BY created_at DESC LIMIT %s"
            with self._connect_pg() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, tuple(params))
                    rows = cur.fetchall()
            return [r[0] for r in rows]

        clauses = ["1=1"]
        params = []
        if topic:
            clauses.append("LOWER(topic) LIKE ?")
            params.append(f"%{topic.lower()}%")
        if class_level is not None:
            clauses.append("class_level = ?")
            params.append(class_level)
        if subject:
            clauses.append("LOWER(subject) = ?")
            params.append(subject.lower())
        params.append(limit)
        sql = f"SELECT metadata_json FROM generated_videos WHERE {' AND '.join(clauses)} ORDER BY created_at DESC LIMIT ?"
        with self._connect_sqlite() as conn:
            rows = conn.execute(sql, tuple(params)).fetchall()
        return [json.loads(r["metadata_json"]) for r in rows]

    def delete_video(self, video_id: str) -> Optional[Dict[str, Any]]:
        existing = self.get_video(video_id)
        if not existing:
            return None
        if self._use_postgres:
            with self._connect_pg() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM generated_videos WHERE video_id = %s", (video_id,))
                conn.commit()
            return existing

        with self._connect_sqlite() as conn:
            conn.execute("DELETE FROM generated_videos WHERE video_id = ?", (video_id,))
        return existing

