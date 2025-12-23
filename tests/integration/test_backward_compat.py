"""Integration tests for backward compatibility."""

import tempfile
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from ord_plan.cli.generate import generate


class TestBackwardCompatibility:
    """Integration tests for backward compatibility with existing workflows."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Fixture for invoking command-line interfaces."""
        return CliRunner()

    def test_combined_rules_file_without_format_flag(self, runner: CliRunner) -> None:
        """Test using combined rules file without --format flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create combined rules file with formatting and events
            rules_content = {
                "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
                "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d %a",
                "REVERSE_DATETREE_YEAR_FORMAT": "%Y",
                "REVERSE_DATETREE_USE_WEEK_TREE": True,
                "events": [
                    {
                        "title": "Weekly Meeting",
                        "cron": "0 14 * * 2",
                        "tags": ["team"],
                    }
                ],
            }
            rules_file = tmpdir_path / "rules.yaml"
            rules_file.write_text(yaml.dump(rules_content))

            # Run generate without --format flag
            result = runner.invoke(
                generate,
                [
                    "--rules",
                    str(rules_file),
                    "--from",
                    "2026-01-01",
                    "--to",
                    "2026-01-31",
                ],
            )

            assert result.exit_code == 0
            assert "Weekly Meeting" in result.output

    def test_events_only_rules_file_without_format_flag(
        self, runner: CliRunner
    ) -> None:
        """Test using events-only rules file without --format flag (uses defaults)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create events-only rules file
            rules_content = {
                "events": [
                    {
                        "title": "Morning Exercise",
                        "cron": "0 7 * * 1,3,5",
                        "tags": ["health"],
                    }
                ]
            }
            rules_file = tmpdir_path / "rules.yaml"
            rules_file.write_text(yaml.dump(rules_content))

            # Run generate without --format flag (uses default formatting)
            result = runner.invoke(
                generate,
                [
                    "--rules",
                    str(rules_file),
                    "--from",
                    "2026-01-01",
                    "--to",
                    "2026-01-31",
                ],
            )

            # Should succeed with default formatting values
            assert result.exit_code == 0
            assert "Morning Exercise" in result.output

    def test_existing_workflow_unchanged(self, runner: CliRunner) -> None:
        """Test that existing workflow (combined rules file) is unchanged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create standard combined rules file
            rules_content = {
                "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
                "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d %a",
                "REVERSE_DATETREE_YEAR_FORMAT": "%Y",
                "REVERSE_DATETREE_USE_WEEK_TREE": True,
                "events": [
                    {
                        "title": "Morning Exercise",
                        "cron": "0 7 * * 1,3,5",
                        "tags": ["health", "exercise"],
                    },
                    {
                        "title": "Team Meeting",
                        "cron": "0 14 * * 2",
                        "tags": ["team"],
                    },
                ],
            }
            rules_file = tmpdir_path / "rules.yaml"
            rules_file.write_text(yaml.dump(rules_content))

            # Run generate the old way (no --format flag)
            result = runner.invoke(
                generate,
                [
                    "--rules",
                    str(rules_file),
                    "--from",
                    "2026-01-01",
                    "--to",
                    "2026-01-31",
                ],
            )

            # Should work exactly as before
            assert result.exit_code == 0
            assert "Morning Exercise" in result.output
            assert "Team Meeting" in result.output
