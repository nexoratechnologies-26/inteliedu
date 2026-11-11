"""Structured logging and secret-redaction utilities for generation jobs."""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


_SECRET_PATTERNS = [
    re.compile(r"(Bearer\s+)[A-Za-z0-9._\-]{8,}", re.IGNORECASE),
    re.compile(r"(gsk_[A-Za-z0-9]{8,})"),
    re.compile(r"(AIza[A-Za-z0-9_\-]{10,})"),
    re.compile(r"(key_[A-Za-z0-9_\-]{10,})"),
    re.compile(r"(eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+)"),
]


def redact_secrets(text: str) -> str:
    """Redact common API key / JWT token patterns from log messages."""
    if not text:
        return text
    sanitized = text
    for pattern in _SECRET_PATTERNS:
        if pattern.groups:
            sanitized = pattern.sub(r"\1[REDACTED]", sanitized)
        else:
            sanitized = pattern.sub("[REDACTED]", sanitized)
    return sanitized


class SecretRedactingFilter(logging.Filter):
    """Logging filter that scrubs sensitive credentials before output."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = redact_secrets(record.msg)
        if record.args:
            record.args = tuple(
                redact_secrets(a) if isinstance(a, str) else a for a in record.args
            )
        return True


def get_logger(name: str = "inteliedu.3d_agent", level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        handler.setFormatter(formatter)
        handler.addFilter(SecretRedactingFilter())
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger


def append_job_log(
    logs: Optional[List[Dict[str, Any]]],
    stage: str,
    message: str,
    level: str = "INFO",
    details: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Return a new log list with a timestamped, secret-scrubbed job log entry."""
    entry: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level.upper(),
        "stage": stage,
        "message": redact_secrets(message),
    }
    if details:
        entry["details"] = details
    updated = list(logs or [])
    updated.append(entry)
    return updated

