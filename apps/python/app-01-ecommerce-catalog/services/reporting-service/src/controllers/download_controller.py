"""Download controller for completed report exports."""

import os

from flask import jsonify, send_file

from ..models.report_job import get_job, JobStatus
from ..services.audit_service import log_download_event
from ..services.export_service import EXPORTS_DIR


def download_report(job_id: str):
    job = get_job(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    if job.status != JobStatus.COMPLETED:
        return jsonify({"error": f"Job status is '{job.status.value}', must be 'completed' to download"}), 404

    if not job.output_path or not os.path.exists(job.output_path):
        return jsonify({"error": "Export file not found"}), 404

    log_download_event(job_id, job.supplier_id)

    filename = f"report_{job.job_id}.{job.output_format}"
    return send_file(job.output_path, as_attachment=True, download_name=filename)
