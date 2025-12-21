"""Org-mode event model for ord-plan."""

from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Optional


@dataclass
class OrgEvent:
    """Represents a single org-mode event."""

    title: str
    level: int = 4  # Default headline level for events
    todo_state: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    description: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate the org event after initialization."""
        if not self.title.strip():
            raise ValueError("Event title cannot be empty")

        if self.level < 1:
            raise ValueError("Event level must be at least 1")
