"""Org-mode date node model for ord-plan."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from .org_event import OrgEvent


@dataclass
class OrgDateNode:
    """Represents a date node in the org-mode hierarchy."""

    date: datetime
    existing_events: List[OrgEvent] = field(default_factory=list)
    new_events: List[OrgEvent] = field(default_factory=list)

    @property
    def year(self) -> str:
        """Get formatted year string."""
        return self.date.strftime("%Y")

    @property
    def week(self) -> str:
        """Get formatted week string."""
        return self.date.strftime("%Y-W%V")

    @property
    def day(self) -> str:
        """Get formatted day string."""
        return self.date.strftime("%Y-%m-%d %a")

    @property
    def all_events(self) -> List[OrgEvent]:
        """Get all events (existing + new)."""
        return self.existing_events + self.new_events
