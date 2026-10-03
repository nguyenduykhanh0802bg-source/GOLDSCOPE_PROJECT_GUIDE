"""Structured (JSON) logging with secret redaction."""

from __future__ import annotations

import json
import logging
import re
import sys
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any

REDACTED = "***"

# query-string / key=value style credentials, e.g. ?apikey=XYZ&symbol=GOLD
_KEY_PARAM = re.compile(
    r"(?i)\b(api[_-]?key|apikey|token|secret|password|key)=([^&\s\"']+)",
)
# user:password@host in connection URLs
_URL_CREDENTIALS = re.compile(r"(?i)\b([a-z][a-z0-9+.\-]*://[^:/\s@]+):([^@\s]+)@")


def redact_text(text: str, secrets: Iterable[str] = ()) -> str:
    """Remove credentials from text destined for logs, errors or evidence files."""
    for secret in secrets:
        if secret:
            text = text.replace(secret, REDACTED)
    text = _KEY_PARAM.sub(lambda m: f"{m.group(1)}={REDACTED}", text)
    return _URL_CREDENTIALS.sub(lambda m: f"{m.group(1)}:{REDACTED}@", text)


class JsonFormatter(logging.Formatter):
    def __init__(self, secrets: Iterable[str] = ()) -> None:
        super().__init__()
        self._secrets = [s for s in secrets if s]

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": redact_text(record.getMessage(), self._secrets),
        }
        if record.exc_info:
            payload["exc"] = redact_text(self.formatException(record.exc_info), self._secrets)
        extra = getattr(record, "fields", None)
        if isinstance(extra, dict):
            payload["fields"] = {
                str(k): redact_text(str(v), self._secrets) for k, v in extra.items()
            }
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str = "INFO", secrets: Iterable[str] = ()) -> logging.Logger:
    """Configure the `goldscope` logger. Idempotent: replaces its handlers."""
    logger = logging.getLogger("goldscope")
    logger.setLevel(level.upper())
    logger.propagate = False
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter(secrets))
    logger.addHandler(handler)
    return logger
