"""File service for handling org-mode file operations."""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, TextIO

from ..models.org_date_node import OrgDateNode
from ..models.org_event import OrgEvent
from ..parsers.org_mode import OrgModeParser


class FileService:
    """Service for handling file operations and content preservation."""

    @staticmethod
    def write_org_content(
        content: str,
        file_path: Optional[str] = None,
        output_stream: Optional[TextIO] = None,
    ) -> None:
        """Write org-mode content to file or stream.

        Args:
            content: Org-mode content to write
            file_path: Target file path (None for stdout)
            output_stream: Output stream (default: sys.stdout)

        Raises:
            PermissionError: Cannot write to target location
            OSError: File system error
        """
        if file_path:
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            # Write to file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            # Write to output stream
            if output_stream is None:
                import sys

                output_stream = sys.stdout

            output_stream.write(content)

    @staticmethod
    def merge_with_existing_content(
        new_date_nodes: List[OrgDateNode],
        existing_file_path: str,
    ) -> List[OrgDateNode]:
        """Merge new events with existing file content.

        Args:
            new_date_nodes: List of new date nodes with events
            existing_file_path: Path to existing org-mode file

        Returns:
            Merged list of OrgDateNode objects
        """
        # Read existing content
        existing_nodes = OrgModeParser.read_existing_content(existing_file_path)

        # Create date lookup for existing nodes (normalize to date for comparison)
        existing_dates = {}
        for node in existing_nodes:
            date_key = (
                node.date.date() if isinstance(node.date, datetime) else node.date
            )
            existing_dates[date_key] = node

        # Merge new events with existing
        merged_nodes = {}

        # First, add all existing nodes
        for existing_node in existing_nodes:
            date_key = (
                existing_node.date.date()
                if hasattr(existing_node.date, "date")
                else existing_node.date
            )
            merged_nodes[date_key] = existing_node

        # Then merge new events
        for new_node in new_date_nodes:
            date_key = (
                new_node.date.date()
                if isinstance(new_node.date, datetime)
                else new_node.date
            )

            if date_key in merged_nodes:
                # Merge events into existing node
                existing_node = merged_nodes[date_key]
                existing_node.new_events.extend(new_node.new_events)
            else:
                # Add as new node
                merged_nodes[date_key] = new_node

        # Convert back to list and sort
        result = list(merged_nodes.values())
        result.sort(
            key=lambda n: n.date.date() if isinstance(n.date, datetime) else n.date
        )

        return result

    @staticmethod
    def ensure_file_writable(file_path: str) -> bool:
        """Check if file can be written to.

        Args:
            file_path: Path to check

        Returns:
            True if writable, False otherwise

        Raises:
            PermissionError: No write permission
            OSError: Invalid path
        """
        path = Path(file_path)

        # Check if parent directory is writable
        if not path.parent.exists():
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as e:
                raise PermissionError(f"Cannot create directory {path.parent}: {e}")

        if path.exists():
            if not os.access(file_path, os.W_OK):
                raise PermissionError(f"File {file_path} is not writable")
        else:
            if not os.access(path.parent, os.W_OK):
                raise PermissionError(f"Directory {path.parent} is not writable")

        return True

    @staticmethod
    def backup_existing_file(file_path: str) -> Optional[str]:
        """Create a backup of existing file.

        Args:
            file_path: Path to backup

        Returns:
            Backup file path or None if no backup needed
        """
        if not Path(file_path).exists():
            return None

        import datetime

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.backup_{timestamp}"

        import shutil

        shutil.copy2(file_path, backup_path)

        return backup_path

    @staticmethod
    def get_file_content_stats(file_path: str) -> Dict[str, int]:
        """Get statistics about file content.

        Args:
            file_path: Path to analyze

        Returns:
            Dictionary with file statistics
        """
        path = Path(file_path)

        if not path.exists():
            return {
                "exists": False,
                "size": 0,
                "lines": 0,
                "events": 0,
            }

        # Read existing content and count events
        existing_nodes = OrgModeParser.read_existing_content(file_path)

        total_events = sum(len(node.existing_events) for node in existing_nodes)

        return {
            "exists": True,
            "size": path.stat().st_size,
            "lines": FileService._count_lines(file_path),
            "events": total_events,
        }

    @staticmethod
    def _count_lines(file_path: str) -> int:
        """Count lines in file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return sum(1 for _ in f)
        except Exception:
            return 0
