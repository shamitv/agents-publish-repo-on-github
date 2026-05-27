"""Report job data model for the reporting service."""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ReportJob:
    """Represents an async report generation job."""
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    report_type: str = ""
    supplier_id: str = ""
    period: str = ""
    status: JobStatus = JobStatus.PENDING
    result_summary: Optional[dict] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


# In-memory job store
JOBS: dict[str, ReportJob] = {}


def create_job(report_type: str, supplier_id: str, period: str = "2025-Q1") -> ReportJob:
    """Create a new report job."""
    job = ReportJob(
        report_type=report_type,
        supplier_id=supplier_id,
        period=period,
    )
    JOBS[job.job_id] = job
    return job


def get_job(job_id: str) -> Optional[ReportJob]:
    """Look up a job by ID."""
    return JOBS.get(job_id)


def update_job_status(job_id: str, status: JobStatus, result: Optional[dict] = None) -> Optional[ReportJob]:
    """Update a job's status and optionally set its result."""
    job = JOBS.get(job_id)
    if not job:
        return None
    job.status = status
    if result:
        job.result_summary = result
    if status in (JobStatus.COMPLETED, JobStatus.FAILED):
        job.completed_at = datetime.utcnow()
    return job