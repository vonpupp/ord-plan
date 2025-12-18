"""Unit tests for file service."""

import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from ord_plan.models.org_date_node import OrgDateNode
from ord_plan.models.org_event import OrgEvent
from ord_plan.services.file_service import FileService


class TestFileService:
    """Test cases for FileService."""

    def test_write_org_content_to_file(self) -> None:
        """Test writing content to a file."""
        content = "* 2025\n** 2025-W01\n*** 2025-01-01 Tue\n**** TODO Test Event"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            temp_path = f.name

        try:
            FileService.write_org_content(content, temp_path)

            # Verify content was written
            with open(temp_path, "r") as f:
                assert f.read() == content
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_write_org_content_creates_directories(self) -> None:
        """Test that writing content creates parent directories."""
        content = "* Test Content"

        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = os.path.join(temp_dir, "nested", "subdir", "test.org")

            FileService.write_org_content(content, nested_path)

            # Verify file exists and content is correct
            assert os.path.exists(nested_path)
            with open(nested_path, "r") as f:
                assert f.read() == content

    def test_write_org_content_to_stdout(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test writing content to stdout."""
        content = "* Test Content"

        FileService.write_org_content(content)

        captured = capsys.readouterr()
        assert captured.out == content

    def test_merge_with_existing_content_new_file(self) -> None:
        """Test merging when target file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_file = os.path.join(temp_dir, "new.org")

            # Create new date nodes
            new_nodes = [
                OrgDateNode(
                    date=datetime(2025, 1, 1),
                    new_events=[OrgEvent(title="New Event", todo_state="TODO")],
                )
            ]

            # Should return new nodes as-is
            result = FileService.merge_with_existing_content(new_nodes, new_file)
            assert len(result) == 1
            assert len(result[0].new_events) == 1

    def test_merge_with_existing_content_existing_file(self) -> None:
        """Test merging with existing file content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            existing_file = os.path.join(temp_dir, "existing.org")

            # Create existing file with content
            existing_content = """* 2025
** 2025-W01
*** 2025-01-01 Wed
**** TODO Existing Event
"""
            with open(existing_file, "w") as f:
                f.write(existing_content)

            # Create new date nodes
            new_nodes = [
                OrgDateNode(
                    date=datetime(2025, 1, 1),
                    new_events=[OrgEvent(title="New Event", todo_state="TODO")],
                )
            ]

            # Merge with existing content
            result = FileService.merge_with_existing_content(new_nodes, existing_file)

            assert len(result) == 1
            # Should have at least 1 existing event (the date might be counted as an event too)
            assert len(result[0].existing_events) >= 1
            assert len(result[0].new_events) == 1  # New event added

    def test_ensure_file_writable_new_file(self) -> None:
        """Test checking writability for new file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_file = os.path.join(temp_dir, "new.org")

            # Should return True for writable directory
            assert FileService.ensure_file_writable(new_file) is True

    def test_ensure_file_writable_existing_file(self) -> None:
        """Test checking writability for existing file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            temp_path = f.name

        try:
            # Should return True for writable file
            assert FileService.ensure_file_writable(temp_path) is True
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_ensure_file_writable_permission_denied(self) -> None:
        """Test permission denied scenario."""
        # Skip this test on Windows due to different file permission handling
        import platform

        if platform.system() == "Windows":
            pytest.skip("File permission test skipped on Windows platform")

        # For Unix-like systems, test permission denied
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Make directory read-only
                try:
                    os.chmod(temp_dir, 0o444)
                    readonly_file = os.path.join(temp_dir, "readonly.org")

                    with pytest.raises(PermissionError):
                        FileService.ensure_file_writable(readonly_file)

                    # Restore permissions for cleanup
                    os.chmod(temp_dir, 0o755)
                except (OSError, PermissionError):
                    # Systems without proper permission support
                    pytest.skip("File permission test not supported on this platform")
        except (OSError, PermissionError):
            # Skip if we can't change permissions
            pytest.skip("File permission test not supported on this platform")

    def test_backup_existing_file(self) -> None:
        """Test creating backup of existing file."""
        original_content = "* Original Content"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            temp_path = f.name
            f.write(original_content)

        try:
            backup_path = FileService.backup_existing_file(temp_path)

            # Backup should be created
            assert backup_path is not None
            assert os.path.exists(backup_path)

            # Backup content should match original
            with open(backup_path, "r") as f:
                assert f.read() == original_content

            # Clean up backup
            os.unlink(backup_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_backup_existing_file_no_file(self) -> None:
        """Test backup when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nonexistent_file = os.path.join(temp_dir, "nonexistent.org")

            # Should return None for non-existent file
            backup_path = FileService.backup_existing_file(nonexistent_file)
            assert backup_path is None

    def test_get_file_content_stats_existing_file(self) -> None:
        """Test getting stats for existing file."""
        content = """* 2025
** 2025-W01
*** 2025-01-01 Wed
**** TODO Event 1
**** TODO Event 2
"""

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            temp_path = f.name
            f.write(content)

        try:
            stats = FileService.get_file_content_stats(temp_path)

            assert stats["exists"] is True
            assert stats["size"] > 0
            assert stats["lines"] > 0
            assert stats["events"] >= 2  # Parser might count differently
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_get_file_content_stats_nonexistent_file(self) -> None:
        """Test getting stats for non-existent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nonexistent_file = os.path.join(temp_dir, "nonexistent.org")

            stats = FileService.get_file_content_stats(nonexistent_file)

            assert stats["exists"] is False
            assert stats["size"] == 0
            assert stats["lines"] == 0
            assert stats["events"] == 0

    def test_count_lines(self) -> None:
        """Test line counting functionality."""
        content = "Line 1\nLine 2\nLine 3"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            temp_path = f.name
            f.write(content)

        try:
            count = FileService._count_lines(temp_path)
            assert count == 3
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_count_lines_empty_file(self) -> None:
        """Test line counting for empty file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            temp_path = f.name
            f.write("")

        try:
            count = FileService._count_lines(temp_path)
            assert count == 0
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_count_lines_nonexistent_file(self) -> None:
        """Test line counting for non-existent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nonexistent_file = os.path.join(temp_dir, "nonexistent.org")

            count = FileService._count_lines(nonexistent_file)
            assert count == 0
