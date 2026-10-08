from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime

from prometheus_client import Counter, Histogram

REQUESTS = Counter("rag_requests_total", "RAG requests", ["operation", "status"])
LATENCY = Histogram("rag_request_duration_seconds", "RAG request latency", ["operation"])
ROUTES = Counter("rag_routes_total", "Retrieval routing decisions", ["route"])


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())
