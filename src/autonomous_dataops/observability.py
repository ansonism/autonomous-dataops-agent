from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

SENSITIVE_KEYS = {
    "approval_token",
    "authorization",
    "connection_string",
    "password",
    "secret",
    "token",
}


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(message)s",
        force=True,
    )


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if key.lower() in SENSITIVE_KEYS else _redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def log_event(event: str, **fields: Any) -> None:
    record = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event": event,
        **_redact(fields),
    }
    logging.getLogger("autonomous_dataops").info(
        json.dumps(record, default=str, sort_keys=True, separators=(",", ":"))
    )
