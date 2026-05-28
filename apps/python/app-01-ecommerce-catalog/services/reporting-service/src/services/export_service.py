"""Export service for CSV and XLSX report generation."""

import csv
import io
import os
import re
from datetime import datetime


EXPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "exports")


def _ensure_exports_dir():
    os.makedirs(EXPORTS_DIR, exist_ok=True)


def _flatten(data: dict, prefix: str = "") -> dict:
    rows = {}
    for key, value in data.items():
        col = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            rows.update(_flatten(value, col))
        elif isinstance(value, list):
            rows[col] = ", ".join(str(v) for v in value)
        else:
            rows[col] = value
    return rows


def export_to_csv(data: dict, job_id: str) -> str:
    _ensure_exports_dir()
    filepath = os.path.join(EXPORTS_DIR, f"{job_id}.csv")

    flat = _flatten(data)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(flat.keys())
        writer.writerow(flat.values())

    return filepath


def export_to_xlsx(data: dict, job_id: str) -> str:
    _ensure_exports_dir()
    filepath = os.path.join(EXPORTS_DIR, f"{job_id}.xlsx")

    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Report"

        flat = _flatten(data)
        ws.append(list(flat.keys()))
        ws.append(list(flat.values()))

        wb.save(filepath)
    except ImportError:
        export_to_csv(data, job_id)
        filepath = filepath.replace(".xlsx", ".csv")

    return filepath


# Decoy safe pattern: whitelist-based filename sanitization
def sanitize_filename(name: str) -> str:
    sanitized = re.sub(r"[^a-zA-Z0-9_.-]", "", name)
    sanitized = sanitized.lstrip(".").lstrip("-")
    if not sanitized:
        sanitized = "export"
    return sanitized[:100]
