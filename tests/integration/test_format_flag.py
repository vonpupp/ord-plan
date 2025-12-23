"""Integration tests for --format flag."""

import tempfile
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from ord_plan.cli.generate import generate


class TestFormatFlagIntegration:
    """Integration tests for format flag functionality."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Fixture for invoking command-line interfaces."""
        return CliRunner()

    def test_separate_format_and_rules_files(self, runner: CliRunner) -> None:
        """Test using separate format and rules files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create format file
            format_content = {
                "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
                "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d %a",
                "REVERSE_DATETREE_YEAR_FORMAT": "%Y",
                "REVERSE_DATETREE_USE_WEEK_TREE": True,
            }
            format_file = tmpdir_path / "format.yaml"
            format_file.write_text(yaml.dump(format_content))

            # Create events-only rules file
            rules_content = {
                "events": [
                    {
                        "title": "Weekly Meeting",
                        "cron": "0 14 * * 2",
                        "tags": ["team"],
                    }
                ]
            }
            rules_file = tmpdir_path / "rules.yaml"
            rules_file.write_text(yaml.dump(rules_content))

            # Run generate with both files
            result = runner.invoke(
                generate,
                [
                    "--format",
                    str(format_file),
                    "--rules",
                    str(rules_file),
                    "--from",
                    "2026-01-01",
                    "--to",
                    "2026-01-31",
                ],
            )

            assert result.exit_code == 0
            # Output should contain the event
            assert "Weekly Meeting" in result.output

    def test_format_file_with_valid_rules_file(self, runner: CliRunner) -> None:
        """Test using format file with events-only rules file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create format file
            format_content = {
                "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
                "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d %a",
                "REVERSE_DATETREE_YEAR_FORMAT": "%Y",
                "REVERSE_DATETREE_USE_WEEK_TREE": True,
            }
            format_file = tmpdir_path / "format.yaml"
            format_file.write_text(yaml.dump(format_content))

            # Create rules file with only events
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

            # Run generate
            result = runner.invoke(
                generate,
                [
                    "--format",
                    str(format_file),
                    "--rules",
                    str(rules_file),
                    "--from",
                    "2026-01-01",
                    "--to",
                    "2026-01-31",
                ],
            )

            assert result.exit_code == 0
            assert "Morning Exercise" in result.output

    def test_empty_format_file_uses_defaults(self, runner: CliRunner) -> None:
        """Test that empty format file uses default formatting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create empty format file
            format_file = tmpdir_path / "format.yaml"
            format_file.write_text("# All formatting options will use defaults\n")

            # Create rules file
            rules_content = {
                "events": [
                    {
                        "title": "Test Event",
                        "cron": "0 9 * * 1",
                    }
                ]
            }
            rules_file = tmpdir_path / "rules.yaml"
            rules_file.write_text(yaml.dump(rules_content))

            # Run generate
            result = runner.invoke(
                generate,
                [
                    "--format",
                    str(format_file),
                    "--rules",
                    str(rules_file),
                    "--from",
                    "2026-01-01",
                    "--to",
                    "2026-01-31",
                ],
            )

            assert result.exit_code == 0
            assert "Test Event" in result.output
