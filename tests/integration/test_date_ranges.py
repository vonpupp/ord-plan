"""Integration tests for date range functionality."""

from pathlib import Path

from click.testing import CliRunner

from ord_plan.cli import cli_group


class TestDateRanges:
    """Test date range flexibility functionality."""

    def test_default_date_range(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test default date range (current week)."""
        rules_file = tmp_path / "rules.yaml"
        rules_file.write_text(
            """
REVERSE_DATETREE_WEEK_FORMAT: "%Y-W%V"
REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d %a"
REVERSE_DATETREE_YEAR_FORMAT: "%Y"
REVERSE_DATETREE_USE_WEEK_TREE: true

events:
  - title: "Daily Task"
    cron: "0 9 * * *"
"""
        )

        result = runner.invoke(
            cli_group,
            [
                "generate",
                "--rules",
                str(rules_file),
                "--from",
                "2025-01-01",
                "--to",
                "2025-01-03",
                "--force",
            ],
        )

        assert result.exit_code == 0
        output = result.output

        # Should contain date structure
        assert "* 2025" in output
        assert "** 2025-W01" in output
        assert (
            "*** 2025-01-01" in output
            or "*** 2025-01-02" in output
            or "*** 2025-01-03" in output
        )

    def test_relative_dates(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test relative date parsing."""
        rules_file = tmp_path / "rules.yaml"
        rules_file.write_text(
            """
REVERSE_DATETREE_WEEK_FORMAT: "%Y-W%V"
REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d %a"
REVERSE_DATETREE_YEAR_FORMAT: "%Y"
REVERSE_DATETREE_USE_WEEK_TREE: true

events:
  - title: "Test Task"
    cron: "0 9 * * *"
"""
        )

        result = runner.invoke(
            cli_group,
            [
                "generate",
                "--rules",
                str(rules_file),
                "--from",
                "today",
                "--to",
                "tomorrow",
            ],
        )

        assert result.exit_code == 0
        output = result.output

        # Should contain events
        assert "TODO Test Task" in output

    def test_next_weekday(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test 'next monday' parsing."""
        rules_file = tmp_path / "rules.yaml"
        rules_file.write_text(
            """
REVERSE_DATETREE_WEEK_FORMAT: "%Y-W%V"
REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d %a"
REVERSE_DATETREE_YEAR_FORMAT: "%Y"
REVERSE_DATETREE_USE_WEEK_TREE: true

events:
  - title: "Monday Meeting"
    cron: "0 14 * * 1"
"""
        )

        result = runner.invoke(
            cli_group,
            [
                "generate",
                "--rules",
                str(rules_file),
                "--from",
                "next monday",
                "--to",
                "next monday",
            ],
            input="y\n",
        )

        assert result.exit_code == 0
        output = result.output

        # Should contain Monday structure
        assert "TODO Monday Meeting" in output
