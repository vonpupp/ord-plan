"""Event service for organizing and managing events."""

import time
from collections import defaultdict
from datetime import datetime
from typing import List
from typing import Optional

from ..models.date_range import DateRange
from ..models.event_rule import EventRule
from ..models.org_date_node import OrgDateNode
from ..models.org_event import OrgEvent
from .cron_service import CronService


class EventService:
    """Service for organizing events by date and managing date nodes."""

    @staticmethod
    def organize_events_by_date(
        events: List[OrgEvent], date_range: DateRange
    ) -> List[OrgDateNode]:
        """Organize events by date into OrgDateNode objects.

        Args:
            events: List of events to organize
            date_range: Date range for context

        Returns:
            List of OrgDateNode objects with events grouped by date
        """
        # Group events by date
        events_by_date = defaultdict(list)

        for event in events:
            # Extract datetime from event title (temporary solution)
            if "@@" in event.title:
                title_parts = event.title.split("@@")
                actual_title = title_parts[0]
                event_datetime_str = title_parts[1]
                event_datetime = datetime.fromisoformat(event_datetime_str)

                # Clean up the title
                event.title = actual_title

                # Group by actual event date
                date_key = event_datetime.date()
            else:
                # Fallback to start_date
                date_key = date_range.start_date.date()

            events_by_date[date_key].append(event)

        # Create OrgDateNode objects
        date_nodes = []
        for date, day_events in sorted(events_by_date.items()):
            date_node = OrgDateNode(
                date=datetime.combine(date, datetime.min.time()),
                new_events=day_events,
            )
            date_nodes.append(date_node)

        return date_nodes

    @staticmethod
    def merge_with_existing_nodes(
        new_nodes: List[OrgDateNode], existing_nodes: List[OrgDateNode]
    ) -> List[OrgDateNode]:
        """Merge new date nodes with existing ones.

        Args:
            new_nodes: New date nodes with events to add
            existing_nodes: Existing date nodes from file

        Returns:
            Merged list of date nodes
        """
        # Create a mapping of date to existing nodes
        existing_by_date = {}
        for node in existing_nodes:
            date_key = node.date.date()
            existing_by_date[date_key] = node

        # Merge new nodes with existing ones
        merged_nodes = []

        # Process new nodes
        for new_node in new_nodes:
            date_key = new_node.date.date()

            if date_key in existing_by_date:
                # Merge with existing node
                existing_node = existing_by_date[date_key]
                existing_node.new_events.extend(new_node.new_events)
                merged_nodes.append(existing_node)
            else:
                # Add as new node
                merged_nodes.append(new_node)

        # Add existing nodes that don't have new events
        for existing_node in existing_nodes:
            date_key = existing_node.date.date()
            if date_key not in [node.date.date() for node in new_nodes]:
                merged_nodes.append(existing_node)

        # Sort by date
        merged_nodes.sort(key=lambda node: node.date)

        return merged_nodes

    @staticmethod
    def generate_complete_event_set(
        rules: List[EventRule],
        date_range: DateRange,
        existing_nodes: Optional[List[OrgDateNode]] = None,
        default_todo_state: str = "TODO",
    ) -> List[OrgDateNode]:
        """Generate complete set of events organized by date.

        Args:
            rules: Event rules to process
            date_range: Date range for event generation
            existing_nodes: Existing date nodes from file (optional)
            default_todo_state: Default TODO state for events

        Returns:
            Complete list of date nodes with all events
        """
        if existing_nodes is None:
            existing_nodes = []

        # Performance monitoring
        start_time = time.time()

        # Generate all events from rules with progress tracking
        events = CronService.generate_all_events(rules, date_range, default_todo_state)

        # Performance check for large event sets
        generation_time = time.time() - start_time
        event_count = len(events)

        if event_count > 1000:
            print(
                f"⚠️  Generated {event_count} events in {generation_time:.2f}s - "
                f"consider using a smaller date range for better performance"
            )
        elif generation_time > 30:  # More than 30 seconds
            print(
                f"⚠️  Event generation took {generation_time:.2f}s for "
                f"{event_count} events - this may indicate performance issues"
            )

        # Organize new events by date with optimization
        start_time = time.time()
        new_nodes = EventService.organize_events_by_date(events, date_range)
        organization_time = time.time() - start_time

        if event_count > 500:
            print(
                f"📊 Organized {event_count} events into {len(new_nodes)} date nodes "
                f"in {organization_time:.2f}s"
            )

        # Merge with existing nodes efficiently
        start_time = time.time()
        merged_nodes = EventService.merge_with_existing_nodes(new_nodes, existing_nodes)
        merge_time = time.time() - start_time

        if len(existing_nodes) > 100:
            print(
                f"🔄 Merged {len(new_nodes)} new nodes with {len(existing_nodes)} "
                f"existing nodes in {merge_time:.2f}s"
            )

        return merged_nodes

    @staticmethod
    def estimate_event_count(rules: List[EventRule], date_range: DateRange) -> int:
        """Estimate the number of events that will be generated.

        Args:
            rules: Event rules to process
            date_range: Date range for estimation

        Returns:
            Estimated number of events
        """
        total_days = (
            date_range.end_date.date() - date_range.start_date.date()
        ).days + 1
        estimated_events = 0

        # This is a rough estimation - actual count may vary based on cron specifics
        for _rule in rules:
            # Simple estimation: assume daily events for now
            # In a real implementation, we'd parse cron patterns more intelligently
            estimated_events += total_days

        return estimated_events

    @staticmethod
    def should_show_performance_warning(
        event_count: int, processing_time: float
    ) -> bool:
        """Determine if performance warning should be shown.

        Args:
            event_count: Number of events processed
            processing_time: Time taken in seconds

        Returns:
            True if warning should be shown
        """
        # Show warning if more than 1000 events OR takes more than 30 seconds
        return event_count > 1000 or processing_time > 30
