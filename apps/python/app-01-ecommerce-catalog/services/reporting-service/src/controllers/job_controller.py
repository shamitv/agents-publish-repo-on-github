"""Job controller for the async report generation queue."""

from flask import jsonify, request

from ..services.job_queue import enqueue
from ..models.report_job import get_job, JobStatus


REPORT_TYPES = ["sales", "inventory_health", "data_quality"]


def enqueue_job():
    data = request.get_json() or {}
    report_type = data.get("report_type", "")
    supplier_id = data.get("supplier_id", "")
    period = data.get("period", "2025-Q1")
    output_format = data.get("output_format", "csv")

    if report_type not in REPORT_TYPES:
        return jsonify({"error": f"Invalid report_type. Must be one of {REPORT_TYPES}"}), 400
    if not supplier_id:
        return jsonify({"error": "supplier_id is required"}), 400
    if output_format not in ("csv", "xlsx"):
        return jsonify({"error": "output_format must be 'csv' or 'xlsx'"}), 400

    job = enqueue(report_type, supplier_id, period, output_format)
    return jsonify({
        "job_id": job.job_id,
        "status": job.status.value,
        "report_type": job.report_type,
        "supplier_id": job.supplier_id,
    }), 201


def get_job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    return jsonify({
        "job_id": job.job_id,
        "status": job.status.value,
        "progress_pct": job.progress_pct,
        "report_type": job.report_type,
        "supplier_id": job.supplier_id,
        "error_message": job.error_message,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    })
