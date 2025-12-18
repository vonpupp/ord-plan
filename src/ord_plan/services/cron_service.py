"""Cron service for processing cron expressions."""

from datetime import datetime
from typing import List

from croniter import croniter

from ..models.date_range import DateRange
from ..models.event_rule import EventRule
from ..models.org_event import OrgEvent


class CronService:
    """Service for processing cron expressions and generating events."""

    @staticmethod
    def generate_events_for_rule(
        rule: EventRule, date_range: DateRange, default_todo_state: str = "TODO"
    ) -> List[OrgEvent]:
        """Generate events for a single rule within a date range.

        Args:
            rule: The event rule to generate events for
            date_range: Date range to generate events within
            default_todo_state: Default TODO state for events

        Returns:
            List of OrgEvent objects
        """
        events = []

        # Validate cron expression
        try:
            cron = croniter(rule.cron, date_range.start_date)
        except ValueError as e:
            raise ValueError(f"Invalid cron expression '{rule.cron}': {e}")

        # Generate all occurrences within the date range
        current_date = cron.get_next(datetime)

        while current_date <= date_range.end_date:
            # Only include events that fall within the date range
            if current_date >= date_range.start_date:
                # Store the datetime in the event title for now (temporary solution)
                # In a proper implementation, we'd extend OrgEvent to have a datetime field
                event_title = f"{rule.title}@@{current_date.isoformat()}"
                event = OrgEvent(
                    title=event_title,
                    todo_state=rule.todo_state or default_todo_state,
                    tags=rule.tags,
                    description=rule.description,
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
        rules: List[EventRule], date_range: DateRange, default_todo_state: str = "TODO"
    ) -> List[OrgEvent]:
        """Generate events for all rules within a date range.

        Args:
            rules: List of event rules
            date_range: Date range to generate events within
            default_todo_state: Default TODO state for events

        Returns:
            List of all OrgEvent objects
        """
        all_events = []

        for rule in rules:
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
