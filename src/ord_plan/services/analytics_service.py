"""Analytics service for extracting data from org-mode files."""

import sys
from datetime import datetime
from typing import TYPE_CHECKING

import pandas as pd  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from ..models.org_date_node import OrgDateNode


class AnalyticsService:
    """Service for analyzing org-mode files and extracting task data."""

    @staticmethod
    def extract_task_data(
        org_files: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        class_filter: str | None = None,
        tag_filter: str | None = None,
    ) -> pd.DataFrame:
        """Extract task data from org-mode files for analysis.

        Args:
            org_files: List of paths to org-mode files
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            class_filter: Optional class UUID to filter tasks
            tag_filter: Optional tag to filter tasks

        Returns:
            pandas DataFrame with extracted task data
        """
        from ..parsers.org_mode import OrgModeParser

        # Process all files and collect DataFrames
        all_dataframes = []

        for org_file in org_files:
            try:
                # Parse org-mode file
                date_nodes = OrgModeParser.read_existing_content(org_file)

                # Extract data from this file's nodes
                file_df = AnalyticsService._extract_from_nodes(
                    date_nodes, org_file, start_date, end_date, class_filter
                )

                # Add to collection if not empty
                if not file_df.empty:
                    all_dataframes.append(file_df)
            except Exception as e:
                # Log error but continue with other files
                print(f"Warning: Failed to process {org_file}: {e}", file=sys.stderr)
                continue

        # Concatenate all DataFrames
        if all_dataframes:
            result_df = pd.concat(all_dataframes, ignore_index=True)
        else:
            result_df = pd.DataFrame()

        # Apply tag filtering if specified (applied to merged results)
        if tag_filter and not result_df.empty:
            # Filter if any tag component matches
            result_df = result_df[
                result_df["tags_components"].apply(
                    lambda tags: any(tag_filter in tag for tag in tags)
                )
            ]

        return result_df

    @staticmethod
    def _extract_from_nodes(
        date_nodes: list["OrgDateNode"],
        source_file: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        class_filter: str | None = None,
    ) -> pd.DataFrame:
        """Extract task data from a list of date nodes.

        Args:
            date_nodes: List of OrgDateNode objects
            source_file: Source file path for tracking
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            class_filter: Optional class UUID to filter tasks

        Returns:
            pandas DataFrame with extracted task data
        """
        """Extract task data from a list of date nodes.

        Args:
            date_nodes: List of OrgDateNode objects
            source_file: Source file path for tracking
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            class_filter: Optional class UUID to filter tasks

        Returns:
            pandas DataFrame with extracted task data
        """
        # Extract data from all events
        task_data = []

        for date_node in date_nodes:
            # Get all events (existing + new)
            all_events = list(date_node.existing_events) + list(date_node.new_events)

            for event in all_events:
                # Extract task date from date_node
                task_date = date_node.date.date()

                # Apply date filtering if specified
                if start_date and task_date < start_date.date():
                    continue
                if end_date and task_date > end_date.date():
                    continue

                # Extract class from properties
                class_uuid = event.properties.get("class", "")

                # Apply class filtering
                if class_filter and class_uuid != class_filter:
                    continue

                # Extract acceptance from properties
                acceptance = event.properties.get("acceptance", "")

                # Extract tags and process nested tags
                tags_full = ":".join(event.tags) + ":" if event.tags else ""
                tags_components = event.tags if event.tags else []

                # Parse tag levels
                tag_levels = AnalyticsService._parse_tag_levels(event.tags)

                # Extract other properties
                backlink = event.properties.get("backlink", "")

                task_data.append(
                    {
                        "date": task_date,
                        "title": event.title,
                        "todo_state": event.todo_state or "TODO",
                        "class": class_uuid,
                        "tags_full": tags_full,
                        "tags_components": tags_components,
                        "tag_level_1": tag_levels.get(0),
                        "tag_level_2": tag_levels.get(1),
                        "tag_level_3": tag_levels.get(2),
                        "acceptance": acceptance,
                        "backlink": backlink,
                        "body": event.body or "",
                        "source_file": source_file,
                    }
                )

        # Create DataFrame
        return pd.DataFrame(task_data)

    @staticmethod
    def _parse_tag_levels(tags: list[str]) -> dict[int, str]:
        """Parse nested tags into levels.

        Args:
            tags: List of tag strings

        Returns:
            Dictionary mapping level (0-indexed) to tag value
        """
        levels = {}
        for tag in tags:
            # Split by colon to get hierarchy
            components = tag.split(":")
            for i, component in enumerate(components):
                if component:  # Skip empty components
                    levels[i] = component
        return levels
