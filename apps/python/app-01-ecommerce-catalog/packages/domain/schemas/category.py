from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CategorySchema:
    id: Optional[int] = None
    name: str = ""
    description: str = ""
