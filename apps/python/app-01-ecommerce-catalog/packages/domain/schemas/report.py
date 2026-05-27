from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ReportRequestSchema:
    supplier_id: int = 0
    report_type: str = ""
    filters: Optional[dict] = None
    date_range: Optional[dict] = None


@dataclass
class ReportJobStatusSchema:
    job_id: str = ""
    status: str = "pending"
    progress: float = 0.0
    download_url: Optional[str] = None
