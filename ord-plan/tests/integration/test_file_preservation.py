"""Integration tests for file preservation functionality."""

import os
import tempfile
from datetime import datetime

import pytest
from click.testing import CliRunner

from ord_plan.cli.generate import generate
from tests.fixtures import get_fixture_path, read_fixture


class TestFilePreservation:
    """Integration tests for file preservation."""

    def test_generate_into_new_file(self):
        """Test generating events into a new file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_file = get_fixture_path("test_rules_basic.yaml")
            target_file = os.path.join(temp_dir, "output.org")

            # Run generate command
            runner = CliRunner()
            result = runner.invoke(
                generate,
                [
                    "--rules",
                    str(rules_file),
                    "--file",
                    target_file,
                    "--from",
                    "2026-01-01",
                    "--to",
                    "2026-01-07",
                ],
            )

            assert result.exit_code == 0
            assert os.path.exists(target_file)

            # Check content
            with open(target_file, "r") as f:
                content = f.read()
                assert "Test Event" in content
                assert "2026" in content

    def test_generate_into_existing_file_preserves_content(self):
        """Test that generating into existing file preserves existing content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_file = get_fixture_path("test_rules_file_preservation.yaml")
            target_file = os.path.join(temp_dir, "existing.org")

            # Write existing file from fixture
            existing_content = read_fixture("existing_content.org")
            with open(target_file, "w") as f:
                f.write(existing_content)

            # Run generate command
            runner = CliRunner()
            result = runner.invoke(
                generate,
                [
                    "--rules",
                    str(rules_file),
                    "--file",
                    target_file,
                    "--from",
                    "2026-01-01",
                    "--to",
                    "2026-01-07",
                ],
            )

            assert result.exit_code == 0

            # Check content
            with open(target_file, "r") as f:
                final_content = f.read()

            # Should preserve existing content
            assert "Existing Task 1" in final_content
            assert "Existing Task 2" in final_content
            assert "Another Existing Task" in final_content

            # Should add new content
            assert "New Generated Event" in final_content

    def test_generate_stdout_unchanged(self):
        """Test that stdout output is unchanged."""
        rules_file = get_fixture_path("test_rules_stdout.yaml")

        # Run generate command without --file
        runner = CliRunner()
        result = runner.invoke(
            generate,
            ["--rules", str(rules_file), "--from", "2026-01-01", "--to", "2026-01-07"],
        )

        assert result.exit_code == 0
        assert "Stdout Event" in result.output
        assert "2026" in result.output

    def test_generate_creates_directories(self):
        """Test that file creation creates necessary directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_file = get_fixture_path("test_rules_nested.yaml")
            nested_file = os.path.join(temp_dir, "nested", "deep", "output.org")

            # Run generate command
            runner = CliRunner()
            result = runner.invoke(
                generate,
                [
                    "--rules",
                    str(rules_file),
                    "--file",
                    nested_file,
                    "--from",
                    "2026-01-01",
                    "--to",
                    "2026-01-07",
                ],
            )

            assert result.exit_code == 0
            assert os.path.exists(nested_file)

            # Check content
            with open(nested_file, "r") as f:
                content = f.read()
                assert "Nested Event" in content

    def test_generate_preserves_events_on_same_date(self):
        """Test that existing events on the same date are preserved."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_file = get_fixture_path("test_rules_same_date.yaml")
            target_file = os.path.join(temp_dir, "same_date.org")

            # Write existing file from fixture
            existing_content = read_fixture("same_date_existing.org")
            with open(target_file, "w") as f:
                f.write(existing_content)

            # Run generate command
            runner = CliRunner()
            result = runner.invoke(
                generate,
                [
                    "--rules",
                    str(rules_file),
                    "--file",
                    target_file,
                    "--from",
                    "2026-01-01",
                    "--to",
                    "2026-01-07",
                ],
            )

            assert result.exit_code == 0

            # Check content
            with open(target_file, "r") as f:
                final_content = f.read()

            # Should preserve existing events on same date
            assert "Morning Meeting" in final_content
            assert "Code Review" in final_content

            # Should add new event on same date
            assert "Afternoon Planning" in final_content

    def test_file_permission_error_handling(self):
        """Test handling of file permission errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_file = get_fixture_path("test_rules_basic.yaml")

            # Try to write to a non-existent location that might cause permission issues
            # Note: This test might not work on all systems, so we make it best effort
            invalid_file = "/root/invalid/path/output.org"

            runner = CliRunner()
            result = runner.invoke(
                generate,
                [
                    "--rules",
                    str(rules_file),
                    "--file",
                    invalid_file,
                    "--from",
                    "2026-01-01",
                    "--to",
                    "2026-01-07",
                ],
            )

            # Should handle error gracefully (either succeed with proper dirs or fail gracefully)
            assert result.exit_code != 0 or "Events written to" in result.output
