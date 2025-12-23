"""Integration tests for edge cases."""

import tempfile
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from ord_plan.cli.generate import generate


class TestEdgeCases:
    """Integration tests for edge case scenarios."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Fixture for invoking command-line interfaces."""
        return CliRunner()

    def test_format_file_with_all_defaults(self, runner: CliRunner) -> None:
        """Test using format file with all default values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create format file with default values
            format_content = {
                "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
                "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d %a",
                "REVERSE_DATETREE_YEAR_FORMAT": "%Y",
                "REVERSE_DATETREE_USE_WEEK_TREE": True,
            }
            format_file = tmpdir_path / "format.yaml"
            format_file.write_text(yaml.dump(format_content))

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

    def test_format_and_rules_both_missing_formatting(self, runner: CliRunner) -> None:
        """Test when both format and rules files miss formatting (should fail)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create format file with no formatting
            format_file = tmpdir_path / "format.yaml"
            format_file.write_text("# Empty format file\n")

            # Create rules file with no formatting
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

            # Should work - uses Configuration defaults
            assert result.exit_code == 0
            assert "Test Event" in result.output
