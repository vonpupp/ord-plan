"""Event rule model for ord-plan."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EventRule:
    """Represents a recurring event definition from YAML configuration."""

    title: str
    cron: str
    tags: list[str] = field(default_factory=list)
    todo_state: Optional[str] = None
    description: Optional[str] = None
    body: Optional[str] = None
    properties: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the event rule after initialization."""
        if not self.title.strip():
            raise ValueError("Event title cannot be empty")

        if not self.cron.strip():
            raise ValueError("Cron expression cannot be empty")

        # Validate tag format
        for tag in self.tags:
            if not tag or " " in tag:
                raise ValueError(
                    f"Invalid tag format: {tag!r}. Tags cannot contain spaces."
                )
