from enum import Enum


class SupplierStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


class ReportType(str, Enum):
    SALES = "sales"
    INVENTORY_HEALTH = "inventory_health"
    DATA_QUALITY = "data_quality"


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ProductLifecycleState(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"
