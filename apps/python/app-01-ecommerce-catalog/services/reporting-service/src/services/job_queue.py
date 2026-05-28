"""Async job queue for report generation using a background thread pool."""

import threading
import time
from typing import Optional

from ..models.report_job import (
    ReportJob, JOBS, create_job, get_job, update_job_status,
    JobStatus,
)
from .aggregation_service import (
    get_sales_report,
    get_inventory_health,
    get_data_quality_report,
)
from .export_service import export_to_csv, export_to_xlsx
from .webhook_retry import webhook_service


def _run_job(job_id: str):
    job = get_job(job_id)
    if not job:
        return

    update_job_status(job_id, JobStatus.RUNNING, progress=10.0)

    filters = {
        "supplier_id": job.supplier_id,
        "period": job.period,
    }

    try:
        update_job_status(job_id, JobStatus.RUNNING, progress=30.0)

        if job.report_type == "sales":
            data = get_sales_report(filters)
        elif job.report_type == "inventory_health":
            data = get_inventory_health(filters)
        elif job.report_type == "data_quality":
            data = get_data_quality_report(filters)
        else:
            raise ValueError(f"Unknown report type: {job.report_type}")

        update_job_status(job_id, JobStatus.RUNNING, progress=60.0)

        if job.output_format == "csv":
            output_path = export_to_csv(data, job.job_id)
        elif job.output_format == "xlsx":
            output_path = export_to_xlsx(data, job.job_id)
        else:
            raise ValueError(f"Unknown output format: {job.output_format}")

        job.output_path = output_path
        update_job_status(job_id, JobStatus.COMPLETED, result=data, progress=100.0)

        for sub in _get_subscriptions(job.supplier_id):
            webhook_service.create_delivery(
                url=sub.callback_url,
                payload={"job_id": job_id, "status": "completed", "supplier_id": job.supplier_id},
                webhook_id=sub.subscription_id,
            )

    except Exception as exc:
        update_job_status(job_id, JobStatus.FAILED, error=str(exc), progress=0.0)


def _get_subscriptions(supplier_id: str) -> list:
    try:
        from ..models.webhook_subscription import get_subscriptions
        return get_subscriptions(supplier_id)
    except ImportError:
        return []


def enqueue(report_type: str, supplier_id: str, period: str = "2025-Q1", output_format: str = "csv") -> ReportJob:
    job = create_job(report_type=report_type, supplier_id=supplier_id, period=period)
    job.output_format = output_format

    thread = threading.Thread(target=_run_job, args=(job.job_id,), daemon=True)
    thread.start()

    return job
