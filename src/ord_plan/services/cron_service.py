"""Cron service for processing cron expressions."""

from datetime import datetime, timedelta

from croniter import croniter

from ..models.date_range import DateRange
from ..models.event_rule import EventRule
from ..models.org_event import OrgEvent


class CronService:
    """Service for processing cron expressions and generating events."""

    @staticmethod
    def generate_events_for_rule(
        rule: EventRule, date_range: DateRange, default_todo_state: str = "TODO"
    ) -> list[OrgEvent]:
        """Generate events for a single rule within a date range.

        Args:
            rule: The event rule to generate events for
            date_range: Date range to generate events within
            default_todo_state: Default TODO state for events

        Returns:
            List of OrgEvent objects

        Raises:
            ValueError: If cron expression is invalid
        """
        events: list[OrgEvent] = []

        # Parse rule-specific date ranges
        rule_from = CronService._parse_iso_date(rule.from_)
        rule_to = CronService._parse_iso_date(rule.to)

        # Calculate effective date range
        # Use rule's "from" if present, otherwise use global start
        effective_start = rule_from if rule_from else date_range.start_date
        # Use rule's "to" if present, otherwise use global end
        effective_end = rule_to if rule_to else date_range.end_date

        # Ensure effective range doesn't extend beyond global range
        effective_start = max(effective_start, date_range.start_date)
        effective_end = min(effective_end, date_range.end_date)

        # Check if effective range is valid
        if effective_start > effective_end:
            # No events can be generated in this range
            return events

        # Determine maximum number of events to generate
        max_count = rule.count if rule.count is not None else float("inf")

        # Validate cron expression
        try:
            # Start one microsecond before effective_start to include events at
            # effective_start
            cron_start_time = effective_start - timedelta(microseconds=1)
            cron = croniter(rule.cron, cron_start_time)
        except ValueError as e:
            raise ValueError(f"Invalid cron expression {rule.cron!r}: {e}") from e

        # Generate all occurrences within the effective date range
        current_date = cron.get_next(datetime)

        while current_date <= effective_end and len(events) < max_count:
            # Only include events that fall within the effective range
            if current_date >= effective_start:
                # Add HH:MM prefix to title, except when both hour and minute are 0
                hour = current_date.hour
                minute = current_date.minute

                if hour == 0 and minute == 0:
                    event_title = f"{rule.title}@@{current_date.isoformat()}"
                else:
                    time_prefix = f"{hour:02d}:{minute:02d}"
                    event_title = (
                        f"{time_prefix} {rule.title}@@{current_date.isoformat()}"
                    )
                event = OrgEvent(
                    title=event_title,
                    todo_state=rule.todo_state or default_todo_state,
                    tags=rule.tags,
                    description=rule.description,
                    body=rule.body,
                    properties=rule.properties,
                )
                events.append(event)

            # Get next occurrence
            try:
                current_date = cron.get_next(datetime)
            except (StopIteration, ValueError):
                break

            # Safety check to prevent infinite loops
            if len(events) > 10000:  # Arbitrary large number
                break

        return events

    @staticmethod
    def generate_all_events(
        rules: list[EventRule], date_range: DateRange, default_todo_state: str = "TODO"
    ) -> list[OrgEvent]:
        """Generate events for all rules within a date range.

        Args:
            rules: List of event rules
            date_range: Date range to generate events within
            default_todo_state: Default TODO state for events

        Returns:
            List of all OrgEvent objects

        Raises:
            ValueError: If any rule has invalid cron expression
        """
        all_events = []

        for rule in rules:
            # Skip disabled rules
            if not rule.enabled:
                continue

            try:
                events = CronService.generate_events_for_rule(
                    rule, date_range, default_todo_state
                )
                all_events.extend(events)
            except ValueError as e:
                # In a full implementation, we'd collect and report all errors
                # For now, re-raise to stop execution
                raise e

        return all_events

    @staticmethod
    def _parse_iso_date(date_str: str | None) -> datetime | None:
        """Parse ISO date string (YYYY-MM-DD) to datetime.

        Args:
            date_str: Date string in YYYY-MM-DD format

        Returns:
            datetime object or None if parsing fails
        """
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return None
