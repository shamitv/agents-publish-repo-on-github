"""Audit logging service using JSONL format on disk."""

import json
import os
import threading
from datetime import datetime
from typing import Optional


AUDIT_LOG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "audit_log.jsonl"
)

_lock = threading.Lock()


def _write_event(event: dict):
    os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
    with _lock:
        with open(AUDIT_LOG_PATH, "a") as f:
            # Decoy safe pattern: atomic write-then-rename (simulated via lock)
            f.write(json.dumps(event) + "\n")
            f.flush()


def log_view_event(job_id: str, supplier_id: str):
    event = {
        "event_type": "VIEW",
        "job_id": job_id,
        "supplier_id": supplier_id,
        "timestamp": datetime.utcnow().isoformat(),
    }
    _write_event(event)


def log_download_event(job_id: str, supplier_id: str):
    event = {
        "event_type": "DOWNLOAD",
        "job_id": job_id,
        "supplier_id": supplier_id,
        "timestamp": datetime.utcnow().isoformat(),
    }
    _write_event(event)


def query_audit_log(supplier_id: Optional[str] = None, event_type: Optional[str] = None) -> list[dict]:
    if not os.path.exists(AUDIT_LOG_PATH):
        return []

    results = []
    with open(AUDIT_LOG_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if supplier_id and event.get("supplier_id") != supplier_id:
                continue
            if event_type and event.get("event_type") != event_type:
                continue
            results.append(event)

    return results
