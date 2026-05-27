"""Portal controller for the supplier dashboard and report listing."""

import uuid
from datetime import datetime
from threading import Thread

from flask import jsonify, request

from ..services.dashboard_service import get_kpi_summary, get_supplier_report_list
from ..services.report_generation_service import (
    generate_sales_report,
    generate_inventory_health_report,
    generate_data_quality_report,
)


# In-memory async job simulation
_JOB_STORE: dict = {}


def _run_job(job_id: str, supplier_id: str, report_type: str, period: str):
    import time
    _JOB_STORE[job_id]["status"] = "running"
    _JOB_STORE[job_id]["progress"] = 30
    time.sleep(0.5)
    _JOB_STORE[job_id]["progress"] = 60
    try:
        if report_type == "sales":
            data = generate_sales_report(supplier_id, period)
        elif report_type == "inventory_health":
            data = generate_inventory_health_report(supplier_id)
        elif report_type == "data_quality":
            data = generate_data_quality_report(supplier_id)
        else:
            raise ValueError(f"Unknown report type: {report_type}")
        _JOB_STORE[job_id]["status"] = "completed"
        _JOB_STORE[job_id]["progress"] = 100
        _JOB_STORE[job_id]["result"] = data
        _JOB_STORE[job_id]["completed_at"] = datetime.utcnow().isoformat()
    except Exception as exc:
        _JOB_STORE[job_id]["status"] = "failed"
        _JOB_STORE[job_id]["error"] = str(exc)


def dashboard():
    supplier_id = request.args.get("supplier_id", "")
    if not supplier_id:
        return jsonify({"error": "supplier_id is required"}), 400

    kpi = get_kpi_summary(supplier_id)
    return jsonify({"kpi": kpi})


def list_reports():
    supplier_id = request.args.get("supplier_id", "")
    if not supplier_id:
        return jsonify({"error": "supplier_id is required"}), 400

    reports = get_supplier_report_list(supplier_id)
    return jsonify({"reports": reports})


def get_feature_flags():
    flags = [
        {"key": "dashboard-v2", "enabled": True},
        {"key": "export-xlsx", "enabled": True},
        {"key": "report-scheduling", "enabled": True},
        {"key": "beta-webhook-retry", "enabled": True},
        {"key": "preview-dark-mode", "enabled": False},
    ]
    return jsonify({"flags": [f for f in flags if f["enabled"]]})


def request_report():
    data = request.get_json() or {}
    supplier_id = data.get("supplier_id", "")
    report_type = data.get("report_type", "")
    period = data.get("period", "2025-Q1")

    if not supplier_id:
        return jsonify({"error": "supplier_id is required"}), 400
    if report_type not in ("sales", "inventory_health", "data_quality"):
        return jsonify({"error": "Invalid report_type"}), 400

    job_id = str(uuid.uuid4())
    _JOB_STORE[job_id] = {
        "job_id": job_id,
        "supplier_id": supplier_id,
        "report_type": report_type,
        "period": period,
        "status": "queued",
        "progress": 0,
        "error": None,
        "result": None,
        "created_at": datetime.utcnow().isoformat(),
        "completed_at": None,
    }

    Thread(target=_run_job, args=(job_id, supplier_id, report_type, period), daemon=True).start()

    return jsonify({"job_id": job_id, "status": "queued"}), 201


def get_job_status(job_id: str):
    job = _JOB_STORE.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify({
        "job_id": job["job_id"],
        "status": job["status"],
        "progress": job["progress"],
        "report_type": job["report_type"],
        "error": job.get("error"),
        "created_at": job.get("created_at"),
        "completed_at": job.get("completed_at"),
    })


def download_report(job_id: str):
    job = _JOB_STORE.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    if job["status"] != "completed":
        return jsonify({"error": f"Job status is '{job['status']}', must be 'completed'"}), 404
    return jsonify({
        "job_id": job_id,
        "supplier_id": job["supplier_id"],
        "report_type": job["report_type"],
        "data": job.get("result"),
        "format": "json",
    })
