"""Integration tests for rule filtering features."""

from pathlib import Path

from ord_plan.models.date_range import DateRange
from ord_plan.parsers.yaml_parser import YamlParser
from ord_plan.services.event_service import EventService


class TestEnabledFiltering:
    """Test enabled field filtering."""

    def test_disabled_rule_generates_no_events(self, tmp_path: Path) -> None:
        """Test that disabled rules generate no events."""
        events_file = tmp_path / "events.yaml"
        events_file.write_text(
            """events:
  - title: "Disabled Event"
    cron: "0 9 * * *"
    enabled: false
"""
        )

        # Parse events
        config = YamlParser.parse_rules_file(str(events_file))
        event_rules = YamlParser.parse_event_rules(config)

        # Create a date range for a week
        from datetime import datetime

        date_range = DateRange(
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 7),
        )

        # Generate events
        date_nodes = EventService.generate_complete_event_set(
            event_rules, date_range, default_todo_state="TODO"
        )

        # Verify no events were generated
        assert len(date_nodes) == 0

    def test_enabled_rule_generates_events(self, tmp_path: Path) -> None:
        """Test that enabled rules generate events."""
        events_file = tmp_path / "events.yaml"
        events_file.write_text(
            """events:
  - title: "Enabled Event"
    cron: "0 9 * * *"
    enabled: true
"""
        )

        # Parse events
        config = YamlParser.parse_rules_file(str(events_file))
        event_rules = YamlParser.parse_event_rules(config)

        # Create a date range for a week
        from datetime import datetime

        date_range = DateRange(
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 7),
        )

        # Generate events
        date_nodes = EventService.generate_complete_event_set(
            event_rules, date_range, default_todo_state="TODO"
        )

        # Verify events were generated
        assert len(date_nodes) > 0
        total_events = sum(len(node.new_events) for node in date_nodes)
        # Note: end_date is Jan 7 00:00:00, so Jan 7 09:00 event is excluded
        assert total_events == 6  # Jan 1-6


class TestDateRangeFiltering:
    """Test from/to date range filtering."""

    def test_from_date_filters_events(self, tmp_path: Path) -> None:
        """Test that from date filters events to start from that date."""
        events_file = tmp_path / "events.yaml"
        events_file.write_text(
            """events:
  - title: "Filtered Event"
    cron: "0 9 * * *"
    from: "2026-01-05"
"""
        )

        # Parse events
        config = YamlParser.parse_rules_file(str(events_file))
        event_rules = YamlParser.parse_event_rules(config)

        # Create a date range for two weeks
        from datetime import datetime

        date_range = DateRange(
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 14),
        )

        # Generate events
        date_nodes = EventService.generate_complete_event_set(
            event_rules, date_range, default_todo_state="TODO"
        )

        # Verify events only start from Jan 5
        total_events = sum(len(node.new_events) for node in date_nodes)
        # Note: end_date is Jan 14 00:00:00, so Jan 14 09:00 event is excluded
        # Should have events from Jan 5-13 = 9 days
        assert total_events == 9

    def test_to_date_filters_events(self, tmp_path: Path) -> None:
        """Test that to date filters events to end before that date."""
        events_file = tmp_path / "events.yaml"
        events_file.write_text(
            """events:
  - title: "Filtered Event"
    cron: "0 9 * * *"
    to: "2026-01-05"
"""
        )

        # Parse events
        config = YamlParser.parse_rules_file(str(events_file))
        event_rules = YamlParser.parse_event_rules(config)

        # Create a date range for two weeks
        from datetime import datetime

        date_range = DateRange(
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 14),
        )

        # Generate events
        date_nodes = EventService.generate_complete_event_set(
            event_rules, date_range, default_todo_state="TODO"
        )

        # Verify events only until Jan 5
        total_events = sum(len(node.new_events) for node in date_nodes)
        # Note: rule to is Jan 5 00:00:00, so Jan 5 09:00 event is excluded
        # Should have events from Jan 1-4 = 4 days
        assert total_events == 4

    def test_from_and_to_filter_events(self, tmp_path: Path) -> None:
        """Test that from and to dates filter events to a range."""
        events_file = tmp_path / "events.yaml"
        events_file.write_text(
            """events:
  - title: "Filtered Event"
    cron: "0 9 * * *"
    from: "2026-01-05"
    to: "2026-01-10"
"""
        )

        # Parse events
        config = YamlParser.parse_rules_file(str(events_file))
        event_rules = YamlParser.parse_event_rules(config)

        # Create a date range for a month
        from datetime import datetime

        date_range = DateRange(
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 31),
        )

        # Generate events
        date_nodes = EventService.generate_complete_event_set(
            event_rules, date_range, default_todo_state="TODO"
        )

        # Verify events only in the specified range
        total_events = sum(len(node.new_events) for node in date_nodes)
        # Note: rule to is Jan 10 00:00:00, so Jan 10 09:00 event is excluded
        # Should have events from Jan 5-9 = 5 days
        assert total_events == 5


class TestCountLimiting:
    """Test count field limiting."""

    def test_count_limits_events(self, tmp_path: Path) -> None:
        """Test that count limits the number of events generated."""
        events_file = tmp_path / "events.yaml"
        events_file.write_text(
            """events:
  - title: "Limited Event"
    cron: "0 9 * * *"
    count: 3
"""
        )

        # Parse events
        config = YamlParser.parse_rules_file(str(events_file))
        event_rules = YamlParser.parse_event_rules(config)

        # Create a date range for a week
        from datetime import datetime

        date_range = DateRange(
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 7),
        )

        # Generate events
        date_nodes = EventService.generate_complete_event_set(
            event_rules, date_range, default_todo_state="TODO"
        )

        # Verify only 3 events were generated
        total_events = sum(len(node.new_events) for node in date_nodes)
        assert total_events == 3

    def test_count_zero_generates_no_events(self, tmp_path: Path) -> None:
        """Test that count zero generates no events."""
        events_file = tmp_path / "events.yaml"
        events_file.write_text(
            """events:
  - title: "No Events"
    cron: "0 9 * * *"
    count: 0
"""
        )

        # Parse events
        config = YamlParser.parse_rules_file(str(events_file))
        event_rules = YamlParser.parse_event_rules(config)

        # Create a date range for a week
        from datetime import datetime

        date_range = DateRange(
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 7),
        )

        # Generate events
        date_nodes = EventService.generate_complete_event_set(
            event_rules, date_range, default_todo_state="TODO"
        )

        # Verify no events were generated
        total_events = sum(len(node.new_events) for node in date_nodes)
        assert total_events == 0


class TestCombinedFiltering:
    """Test combined filtering with multiple fields."""

    def test_enabled_and_count(self, tmp_path: Path) -> None:
        """Test enabled with count limiting."""
        events_file = tmp_path / "events.yaml"
        events_file.write_text(
            """events:
  - title: "Limited Enabled Event"
    cron: "0 9 * * *"
    enabled: true
    count: 2
"""
        )

        # Parse events
        config = YamlParser.parse_rules_file(str(events_file))
        event_rules = YamlParser.parse_event_rules(config)

        # Create a date range for a week
        from datetime import datetime

        date_range = DateRange(
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 7),
        )

        # Generate events
        date_nodes = EventService.generate_complete_event_set(
            event_rules, date_range, default_todo_state="TODO"
        )

        # Verify only 2 events were generated
        total_events = sum(len(node.new_events) for node in date_nodes)
        assert total_events == 2

    def test_all_filters_combined(self, tmp_path: Path) -> None:
        """Test all filters combined."""
        events_file = tmp_path / "events.yaml"
        events_file.write_text(
            """events:
  - title: "Fully Filtered Event"
    cron: "0 9 * * *"
    enabled: true
    from: "2026-01-05"
    to: "2026-01-10"
    count: 3
"""
        )

        # Parse events
        config = YamlParser.parse_rules_file(str(events_file))
        event_rules = YamlParser.parse_event_rules(config)

        # Create a date range for a month
        from datetime import datetime

        date_range = DateRange(
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 31),
        )

        # Generate events
        date_nodes = EventService.generate_complete_event_set(
            event_rules, date_range, default_todo_state="TODO"
        )

        # Verify only 3 events were generated
        # (from Jan 5-10 would be 6 days, but count limits to 3)
        total_events = sum(len(node.new_events) for node in date_nodes)
        assert total_events == 3

    def test_disabled_with_other_filters(self, tmp_path: Path) -> None:
        """Test that disabled overrides all other filters."""
        events_file = tmp_path / "events.yaml"
        events_file.write_text(
            """events:
  - title: "Disabled Event"
    cron: "0 9 * * *"
    enabled: false
    from: "2026-01-01"
    to: "2026-01-31"
    count: 10
"""
        )

        # Parse events
        config = YamlParser.parse_rules_file(str(events_file))
        event_rules = YamlParser.parse_event_rules(config)

        # Create a date range for a month
        from datetime import datetime

        date_range = DateRange(
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 31),
        )

        # Generate events
        date_nodes = EventService.generate_complete_event_set(
            event_rules, date_range, default_todo_state="TODO"
        )

        # Verify no events were generated
        assert len(date_nodes) == 0


class TestEdgeCases:
    """Test edge cases for filtering."""

    def test_from_after_to_generates_no_events(self, tmp_path: Path) -> None:
        """Test that from after to generates no events."""
        events_file = tmp_path / "events.yaml"
        events_file.write_text(
            """events:
  - title: "Invalid Range Event"
    cron: "0 9 * * *"
    from: "2026-01-10"
    to: "2026-01-01"
"""
        )

        # Parse events
        config = YamlParser.parse_rules_file(str(events_file))
        event_rules = YamlParser.parse_event_rules(config)

        # Create a date range for a month
        from datetime import datetime

        date_range = DateRange(
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 31),
        )

        # Generate events
        date_nodes = EventService.generate_complete_event_set(
            event_rules, date_range, default_todo_state="TODO"
        )

        # Verify no events were generated
        total_events = sum(len(node.new_events) for node in date_nodes)
        assert total_events == 0

    def test_range_outside_global_range(self, tmp_path: Path) -> None:
        """Test range outside global date range."""
        events_file = tmp_path / "events.yaml"
        events_file.write_text(
            """events:
  - title: "Outside Range Event"
    cron: "0 9 * * *"
    from: "2026-02-01"
    to: "2026-02-10"
"""
        )

        # Parse events
        config = YamlParser.parse_rules_file(str(events_file))
        event_rules = YamlParser.parse_event_rules(config)

        # Create a date range for January
        from datetime import datetime

        date_range = DateRange(
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 31),
        )

        # Generate events
        date_nodes = EventService.generate_complete_event_set(
            event_rules, date_range, default_todo_state="TODO"
        )

        # Verify no events were generated (range is outside global range)
        total_events = sum(len(node.new_events) for node in date_nodes)
        assert total_events == 0
