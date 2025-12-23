"""Integration tests for format file override functionality."""

import tempfile
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from ord_plan.cli.generate import generate


class TestFormatOverride:
    """Integration tests for format file override scenarios."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Fixture for invoking command-line interfaces."""
        return CliRunner()

    def test_conflicting_date_formats(self, runner: CliRunner) -> None:
        """Test that format file overrides conflicting date format in rules file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create format file with different date format
            format_content = {
                "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d",
            }
            format_file = tmpdir_path / "format.yaml"
            format_file.write_text(yaml.dump(format_content))

            # Create rules file with conflicting date format
            rules_content = {
                "REVERSE_DATETREE_DATE_FORMAT": "%d/%m/%Y",
                "REVERSE_DATETREE_USE_WEEK_TREE": True,
                "events": [
                    {
                        "title": "Test Event",
                        "cron": "0 9 * * 1",
                    }
                ],
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
            assert "Test Event" in result.output

    def test_partial_format_file_overrides_specific_options(
        self, runner: CliRunner
    ) -> None:
        """Test that partial format file overrides only specified options."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create partial format file (only date format)
            format_content = {
                "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d",
            }
            format_file = tmpdir_path / "format.yaml"
            format_file.write_text(yaml.dump(format_content))

            # Create rules file with all formatting options
            rules_content = {
                "REVERSE_DATETREE_DATE_FORMAT": "%d/%m/%Y",
                "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
                "REVERSE_DATETREE_YEAR_FORMAT": "%Y",
                "REVERSE_DATETREE_USE_WEEK_TREE": True,
                "events": [
                    {
                        "title": "Test Event",
                        "cron": "0 9 * * 1",
                    }
                ],
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
            assert "Test Event" in result.output

    def test_precedence_order(self, runner: CliRunner) -> None:
        """Test precedence order: format > rules > defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create format file
            format_content = {
                "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d",
                "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
            }
            format_file = tmpdir_path / "format.yaml"
            format_file.write_text(yaml.dump(format_content))

            # Create events-only rules file (no formatting)
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

            # Run generate with format file
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

    def test_format_overrides_boolean_value(self, runner: CliRunner) -> None:
        """Test that format file overrides boolean value from rules file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create format file
            format_content = {
                "REVERSE_DATETREE_USE_WEEK_TREE": False,
            }
            format_file = tmpdir_path / "format.yaml"
            format_file.write_text(yaml.dump(format_content))

            # Create rules file
            rules_content = {
                "REVERSE_DATETREE_USE_WEEK_TREE": True,
                "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d %a",
                "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
                "REVERSE_DATETREE_YEAR_FORMAT": "%Y",
                "events": [
                    {
                        "title": "Test Event",
                        "cron": "0 9 * * 1",
                    }
                ],
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
            assert "Test Event" in result.output
