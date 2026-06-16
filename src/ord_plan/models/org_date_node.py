"""Org-mode date node model for ord-plan."""

from dataclasses import dataclass, field
from datetime import datetime

from .org_event import OrgEvent


@dataclass
class OrgDateNode:
    """Represents a date node in the org-mode hierarchy."""

    date: datetime
    existing_events: list[OrgEvent] = field(default_factory=list)
    new_events: list[OrgEvent] = field(default_factory=list)

    @property
    def year(self) -> str:
        """Get formatted year string."""
        return self.date.strftime("%Y")

    @property
    def week(self) -> str:
        """Get formatted week string."""
        iso_week = int(self.date.strftime("%V"))
        year = self.date.year
        week = iso_week - 1
        if week == 0:
            # Handle week 0 by going to last week of previous year
            prev_year = year - 1
            dec_31 = datetime(prev_year, 12, 31)
            week = int(dec_31.strftime("%V"))
            year = prev_year
        return f"{year}-W{week:02d}"

    @property
    def day(self) -> str:
        """Get formatted day string."""
        return self.date.strftime("%Y-%m-%d %a")

    @property
    def all_events(self) -> list[OrgEvent]:
        """Get all events (existing + new)."""
        return self.existing_events + self.new_events
