"""Integration tests for properties feature."""

from pathlib import Path

from ord_plan.models.date_range import DateRange
from ord_plan.parsers.yaml_parser import YamlParser
from ord_plan.services.event_service import EventService


class TestPropertiesRendering:
    """Test properties rendering in org-mode output."""

    def test_properties_drawer_rendering(self, tmp_path: Path) -> None:
        """Test that properties are rendered as PROPERTIES drawer."""
        events_file = tmp_path / "events.yaml"
        events_file.write_text(
            """events:
  - title: "Test Event"
    cron: "0 9 * * *"
    properties:
      - category: test
      - priority: high
"""
        )

        # Parse events
        config = YamlParser.parse_rules_file(str(events_file))
        event_rules = YamlParser.parse_event_rules(config)

        # Create a date range for a single day (include full day)
        from datetime import datetime

        date_range = DateRange(
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 1, 23, 59, 59),
        )

        # Generate events
        date_nodes = EventService.generate_complete_event_set(
            event_rules, date_range, default_todo_state="TODO"
        )

        # Render org content
        from ord_plan.parsers.org_mode import OrgModeParser

        org_content = OrgModeParser.render_org_content(date_nodes)

        # Verify PROPERTIES drawer is present
        assert ":PROPERTIES:" in org_content
        assert ":CATEGORY: test" in org_content
        assert ":PRIORITY: high" in org_content
        assert ":END:" in org_content

    def test_properties_with_body(self, tmp_path: Path) -> None:
        """Test that properties come before body in event rendering."""
        events_file = tmp_path / "events.yaml"
        events_file.write_text(
            """events:
  - title: "Test Event"
    cron: "0 9 * * *"
    properties:
      - category: test
    body: |
      This is the body
      with multiple lines
"""
        )

        # Parse events
        config = YamlParser.parse_rules_file(str(events_file))
        event_rules = YamlParser.parse_event_rules(config)

        # Create a date range for a single day (include full day)
        from datetime import datetime

        date_range = DateRange(
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 1, 23, 59, 59),
        )

        # Generate events
        date_nodes = EventService.generate_complete_event_set(
            event_rules, date_range, default_todo_state="TODO"
        )

        # Render org content
        from ord_plan.parsers.org_mode import OrgModeParser

        org_content = OrgModeParser.render_org_content(date_nodes)

        # Verify ordering: heading -> properties -> body
        lines = org_content.split("\n")

        heading_idx = None
        properties_idx = None
        end_idx = None
        body_idx = None

        for i, line in enumerate(lines):
            if line.startswith("**** TODO Test Event"):
                heading_idx = i
            if ":PROPERTIES:" in line:
                properties_idx = i
            if ":END:" in line:
                end_idx = i
            if "This is the body" in line:
                body_idx = i

        assert heading_idx is not None, "Heading not found"
        assert properties_idx is not None, "Properties not found"
        assert end_idx is not None, "END not found"
        assert body_idx is not None, "Body not found"

        # Verify ordering
        assert heading_idx < properties_idx, "Properties should come after heading"
        assert properties_idx < end_idx, "END should come after PROPERTIES"
        assert end_idx < body_idx, "Body should come after END"

    def test_properties_with_special_values(self, tmp_path: Path) -> None:
        """Test that properties with special values are rendered correctly."""
        events_file = tmp_path / "events.yaml"
        events_file.write_text(
            """events:
  - title: "Test Event"
    cron: "0 9 * * *"
    properties:
      - backlink: "[[id:da2b6c68-073b-45be-af3b-53796df16a04][goal:health]]"
      - acceptance: "check_habit('1/180d')"
"""
        )

        # Parse events
        config = YamlParser.parse_rules_file(str(events_file))
        event_rules = YamlParser.parse_event_rules(config)

        # Create a date range for a single day (include full day)
        from datetime import datetime

        date_range = DateRange(
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 1, 23, 59, 59),
        )

        # Generate events
        date_nodes = EventService.generate_complete_event_set(
            event_rules, date_range, default_todo_state="TODO"
        )

        # Render org content
        from ord_plan.parsers.org_mode import OrgModeParser

        org_content = OrgModeParser.render_org_content(date_nodes)

        # Verify special values are preserved
        assert (
            ":BACKLINK: [[id:da2b6c68-073b-45be-af3b-53796df16a04][goal:health]]"
            in org_content
        )
        assert ":ACCEPTANCE: check_habit('1/180d')" in org_content

    def test_event_without_properties(self, tmp_path: Path) -> None:
        """Test that events without properties work correctly."""
        events_file = tmp_path / "events.yaml"
        events_file.write_text(
            """events:
  - title: "Simple Event"
    cron: "0 9 * * *"
"""
        )

        # Parse events
        config = YamlParser.parse_rules_file(str(events_file))
        event_rules = YamlParser.parse_event_rules(config)

        # Create a date range for a single day (include full day)
        from datetime import datetime

        date_range = DateRange(
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 1, 23, 59, 59),
        )

        # Generate events
        date_nodes = EventService.generate_complete_event_set(
            event_rules, date_range, default_todo_state="TODO"
        )

        # Render org content
        from ord_plan.parsers.org_mode import OrgModeParser

        org_content = OrgModeParser.render_org_content(date_nodes)

        # Verify no PROPERTIES drawer
        assert ":PROPERTIES:" not in org_content
        assert ":END:" not in org_content  # No END without properties

        # But event should still be present
        assert "Simple Event" in org_content


class TestPropertiesParsing:
    """Test parsing properties from existing org-mode files."""

    def test_parse_properties_from_org_file(self, tmp_path: Path) -> None:
        """Test that properties are parsed from existing org-mode files."""
        org_file = tmp_path / "existing.org"
        org_file.write_text(
            """* 2026
** 2026-W01
*** 2026-01-01 Thu
**** TODO Test Event :test:
:PROPERTIES:
:BACKLINK: [[id:da2b6c68-073b-45be-af3b-53796df16a04][goal:health]]
:ACCEPTANCE: check_habit('1/180d')
:END:
Body text
"""
        )

        # Parse existing content
        from ord_plan.parsers.org_mode import OrgModeParser

        existing_nodes = OrgModeParser.read_existing_content(str(org_file))

        # Verify properties are parsed
        assert len(existing_nodes) > 0
        date_node = existing_nodes[0]
        assert len(date_node.existing_events) > 0

        event = date_node.existing_events[0]
        assert "backlink" in event.properties
        expected_backlink = "[[id:da2b6c68-073b-45be-af3b-53796df16a04][goal:health]]"
        assert event.properties["backlink"] == expected_backlink
        assert "acceptance" in event.properties
        assert event.properties["acceptance"] == "check_habit('1/180d')"

    def test_parse_event_without_properties(self, tmp_path: Path) -> None:
        """Test that events without properties are parsed correctly."""
        org_file = tmp_path / "existing.org"
        org_file.write_text(
            """* 2026
** 2026-W01
*** 2026-01-01 Thu
**** TODO Simple Event :test:
Body text
"""
        )

        # Parse existing content
        from ord_plan.parsers.org_mode import OrgModeParser

        existing_nodes = OrgModeParser.read_existing_content(str(org_file))

        # Verify event is parsed without properties
        assert len(existing_nodes) > 0
        date_node = existing_nodes[0]
        assert len(date_node.existing_events) > 0

        event = date_node.existing_events[0]
        assert event.properties == {}


class TestPropertiesPreservation:
    """Test that properties are preserved during regeneration."""

    def test_properties_preserved_in_regeneration(self, tmp_path: Path) -> None:
        """Test that properties from existing events are preserved."""
        # Create existing org file with properties
        org_file = tmp_path / "existing.org"
        org_file.write_text(
            """* 2026
** 2026-W01
*** 2026-01-01 Thu
**** TODO Existing Event :existing:
:PROPERTIES:
:CATEGORY: test
:END:
Existing body
"""
        )

        # Create events file
        events_file = tmp_path / "events.yaml"
        events_file.write_text(
            """events:
  - title: "Existing Event"
    cron: "0 9 1 1 *"
    tags: ["existing"]
    properties:
      - category: test
    body: |
      Existing body
"""
        )

        # Parse existing content
        from ord_plan.parsers.org_mode import OrgModeParser

        existing_nodes = OrgModeParser.read_existing_content(str(org_file))

        # Parse new events
        config = YamlParser.parse_rules_file(str(events_file))
        event_rules = YamlParser.parse_event_rules(config)

        # Create a date range
        from datetime import datetime

        date_range = DateRange(
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 1),
        )

        # Generate events with existing nodes
        date_nodes = EventService.generate_complete_event_set(
            event_rules,
            date_range,
            existing_nodes=existing_nodes,
            default_todo_state="TODO",
        )

        # Render org content
        org_content = OrgModeParser.render_org_content(date_nodes)

        # Verify properties are preserved
        assert ":PROPERTIES:" in org_content
        assert ":CATEGORY: test" in org_content
        assert ":END:" in org_content
