"""Date range model for ord-plan."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List


@dataclass
class DateRange:
    """Defines the time period for event generation."""

    start_date: datetime
    end_date: datetime
    warnings: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate date range after initialization."""
        if self.start_date > self.end_date:
            raise ValueError("Start date must be before or equal to end date")

        # Enhanced date protection checks
        self._check_past_dates()
        self._check_future_dates()

    def _check_past_dates(self) -> None:
        """Check for past dates and add appropriate warnings."""
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(
            days=now.weekday()
        )  # Monday of current week

        # Only warn about dates before the current week
        if self.start_date < week_start:
            days_past = (week_start - self.start_date).days

            if days_past > 365:
                self.warnings.append(
                    f"Generating events for dates more than 1 year in the past ({days_past} days ago)"
                )
            elif days_past > 30:
                self.warnings.append(
                    f"Generating events for dates more than 1 month in the past ({days_past} days ago)"
                )
            elif days_past > 7:
                self.warnings.append(
                    f"Generating events for dates more than 1 week in the past ({days_past} days ago)"
                )
            else:
                self.warnings.append(
                    f"Generating events for past dates ({days_past} days ago)"
                )

    def _check_future_dates(self) -> None:
        """Check for future dates beyond 1 year and add warnings."""
        now = datetime.now()
        one_year_future = now.replace(year=now.year + 1, month=now.month, day=now.day)

        if self.end_date > one_year_future:
            years_future = (self.end_date.year - now.year) + (
                self.end_date - self.end_date.replace(year=now.year)
            ).days / 365.25

            if years_future > 2:
                self.warnings.append(
                    f"Generating events more than 2 years in the future ({years_future:.1f} years from now)"
                )
            else:
                self.warnings.append(
                    f"Generating events beyond 1 year in the future ({years_future:.1f} years from now)"
                )

    def has_past_dates(self) -> bool:
        """Check if date range includes past dates."""
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(
            days=now.weekday()
        )  # Monday of current week
        return self.start_date < week_start

    def has_distant_future_dates(self) -> bool:
        """Check if date range extends beyond 1 year in future."""
        now = datetime.now()
        one_year_future = now.replace(year=now.year + 1)
        return self.end_date > one_year_future
