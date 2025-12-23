"""Org-mode parser and renderer for ord-plan."""

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import orgparse

from ..models.org_date_node import OrgDateNode
from ..models.org_event import OrgEvent


class OrgModeParser:
    """Parser and renderer for org-mode files."""

    @staticmethod
    def read_existing_content(file_path: str) -> List[OrgDateNode]:
        """Read existing org-mode content and extract events.

        Args:
            file_path: Path to the org-mode file

        Returns:
            List of OrgDateNode objects with existing events
        """
        try:
            with open(file_path) as f:
                root = orgparse.load(f)
        except FileNotFoundError:
            return []

        date_nodes = []

        for node in root[1:]:  # Skip root node
            if node.heading and OrgModeParser._is_date_node(node):
                date_node = OrgModeParser._parse_date_node(node)
                if date_node:
                    date_nodes.append(date_node)

        return date_nodes

    @staticmethod
    def render_org_content(date_nodes: List[OrgDateNode]) -> str:
        """Render org-mode content from date nodes.

        Args:
            date_nodes: List of OrgDateNode objects

        Returns:
            Formatted org-mode content as string
        """
        if not date_nodes:
            return ""

        lines = []

        # Group by year and week
        year_weeks: Dict[Tuple[str, str], List[OrgDateNode]] = {}
        for node in date_nodes:
            year_week_key = (node.year, node.week)
            if year_week_key not in year_weeks:
                year_weeks[year_week_key] = []
            year_weeks[year_week_key].append(node)

        # Sort by year and week
        sorted_year_weeks = sorted(year_weeks.keys())

        current_year = None

        for year, week in sorted_year_weeks:
            nodes_in_week = sorted(year_weeks[(year, week)], key=lambda n: n.date)

            # Add year heading if needed
            if year != current_year:
                if current_year is not None:
                    lines.append("")  # Empty line between years
                lines.append(f"* {year}")
                current_year = year

            # Add week heading
            lines.append(f"** {week}")

            # Add date nodes and events
            for node in nodes_in_week:
                lines.append(f"*** {node.day}")

                # Add existing events
                for event in node.existing_events:
                    lines.append(OrgModeParser._render_event(event))

                # Add new events
                for event in node.new_events:
                    lines.append(OrgModeParser._render_event(event))

        return "\n".join(lines)

    @staticmethod
    def _is_date_node(node: Any) -> bool:
        """Check if a node represents a date."""
        # A date node typically has a heading that looks like a date
        # This is a simple implementation - could be enhanced
        heading = node.heading
        if not heading:
            return False

        # Simple check for YYYY-MM-DD format
        import re

        return bool(re.match(r"\d{4}-\d{2}-\d{2}", heading))

    @staticmethod
    def _parse_date_node(node: Any) -> Optional[OrgDateNode]:
        """Parse a date node from orgparse node."""
        try:
            # Extract date from heading - this is simplified
            # In a full implementation, this would be more robust
            import datetime
            import re

            heading = node.heading
            match = re.match(r"(\d{4})-(\d{2})-(\d{2})", heading)
            if not match:
                return None

            year, month, day = map(int, match.groups())
            date = datetime.datetime(year, month, day)
            date_node = OrgDateNode(date)

            # Parse events under this date node
            for child in node:
                if child.heading:
                    event = OrgModeParser._parse_event_from_node(child)
                    if event:
                        date_node.existing_events.append(event)

            return date_node
        except Exception:
            # If parsing fails, return None
            return None

    @staticmethod
    def _parse_event_from_node(node: Any) -> Optional[OrgEvent]:
        """Parse an event from orgparse node."""
        heading = node.heading
        if not heading:
            return None

        # Extract TODO state if present
        todo_state = None
        title = heading

        if heading.startswith(("TODO ", "DONE ", "INPROGRESS ")):
            parts = heading.split(" ", 1)
            todo_state = parts[0]
            title = parts[1] if len(parts) > 1 else ""

        # Extract tags from heading
        tags = list(node.tags) if hasattr(node, "tags") else []

        # Get body content as body
        body = None
        if node.body:
            body = "\n".join(str(line) for line in node.body)
            body = body.strip() or None

        return OrgEvent(
            title=title.strip(),
            todo_state=todo_state,
            tags=tags,
            body=body,
        )

    @staticmethod
    def _render_event(event: OrgEvent) -> str:
        """Render an event as an org-mode heading."""
        parts = []

        # Add TODO state if present
        if event.todo_state:
            parts.append(event.todo_state)

        # Add title
        parts.append(event.title)

        # Add tags if present
        if event.tags:
            tag_str = ":" + ":".join(event.tags) + ":"
            parts.append(tag_str)

        heading = "*" * event.level + " " + " ".join(parts)

        # Add body if present
        if event.body:
            heading += "\n" + event.body.rstrip()

        return heading
