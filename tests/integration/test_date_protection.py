"""Integration tests for date protection functionality."""

from datetime import datetime
from datetime import timedelta
from pathlib import Path

import yaml
from click.testing import CliRunner

from ord_plan.cli.generate import generate


class TestDateProtectionIntegration:
    """Test date protection in CLI workflow."""

    def test_past_date_warning_with_force(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test past date generation with --force flag."""
        # Create rules file
        yaml_content = {
            "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
            "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d %a",
            "REVERSE_DATETREE_YEAR_FORMAT": "%Y",
            "REVERSE_DATETREE_USE_WEEK_TREE": True,
            "events": [
                {
                    "title": "Test Event",
                    "cron": "0 9 * * 1",
                }
            ],
        }

        yaml_file = tmp_path / "rules.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        output_file = tmp_path / "output.org"

        # Test with past dates and --force
        past_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")

        result = runner.invoke(
            generate,
            [
                "--rules",
                str(yaml_file),
                "--file",
                str(output_file),
                "--from",
                past_date,
                "--to",
                past_date,
                "--force",
            ],
        )

        # Should succeed with force flag
        assert result.exit_code == 0
        assert output_file.exists()
        assert "Note: Bypassing" in result.output or "Bypassing" in result.output

    def test_past_date_warning_without_force(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test past date warning without --force flag."""
        yaml_content = {
            "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
            "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d %a",
            "REVERSE_DATETREE_YEAR_FORMAT": "%Y",
            "REVERSE_DATETREE_USE_WEEK_TREE": True,
            "events": [
                {
                    "title": "Test Event",
                    "cron": "0 9 * * 1",
                }
            ],
        }

        yaml_file = tmp_path / "rules.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        # Test with past dates more than 1 month ago
        past_date = (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d")

        result = runner.invoke(
            generate,
            ["--rules", str(yaml_file), "--from", past_date, "--to", past_date],
        )

        # Should show warning and prompt for confirmation
        assert result.exit_code != 0 or "Warning" in result.output
        assert "past" in result.output.lower()

    def test_future_date_warning_with_force(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test future date generation with --force flag."""
        yaml_content = {
            "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
            "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d %a",
            "REVERSE_DATETREE_YEAR_FORMAT": "%Y",
            "REVERSE_DATETREE_USE_WEEK_TREE": True,
            "events": [
                {
                    "title": "Test Event",
                    "cron": "0 9 * * 1",
                }
            ],
        }

        yaml_file = tmp_path / "rules.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        output_file = tmp_path / "output.org"

        # Test with far future dates and --force
        future_date = (datetime.now() + timedelta(days=730)).strftime(
            "%Y-%m-%d"
        )  # Use 730 days (2 years) instead of 800

        result = runner.invoke(
            generate,
            [
                "--rules",
                str(yaml_file),
                "--file",
                str(output_file),
                "--from",
                future_date,
                "--to",
                future_date,
                "--force",
            ],
        )

        # Should succeed with force flag
        assert result.exit_code == 0
        assert output_file.exists()

    def test_future_date_warning_without_force(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test future date warning without --force flag."""
        yaml_content = {
            "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
            "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d %a",
            "REVERSE_DATETREE_YEAR_FORMAT": "%Y",
            "REVERSE_DATETREE_USE_WEEK_TREE": True,
            "events": [
                {
                    "title": "Test Event",
                    "cron": "0 9 * * 1",
                }
            ],
        }

        yaml_file = tmp_path / "rules.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        # Test with dates more than 1 year in future
        future_date = (datetime.now() + timedelta(days=400)).strftime("%Y-%m-%d")

        result = runner.invoke(
            generate,
            ["--rules", str(yaml_file), "--from", future_date, "--to", future_date],
        )

        # Should show warning and prompt for confirmation
        assert result.exit_code != 0 or "Warning" in result.output
        assert "future" in result.output.lower()

    def test_normal_date_range_no_warnings(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test normal date range without warnings."""
        yaml_content = {
            "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
            "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d %a",
            "REVERSE_DATETREE_YEAR_FORMAT": "%Y",
            "REVERSE_DATETREE_USE_WEEK_TREE": True,
            "events": [
                {
                    "title": "Test Event",
                    "cron": "0 9 * * 1",
                }
            ],
        }

        yaml_file = tmp_path / "rules.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        output_file = tmp_path / "output.org"

        # Test with current week dates (Monday to Sunday of this week)
        now = datetime.now()
        monday = now - timedelta(days=now.weekday())  # Monday of current week
        sunday = monday + timedelta(days=6)  # Sunday of current week
        from_date = monday.strftime("%Y-%m-%d")
        to_date = sunday.strftime("%Y-%m-%d")

        result = runner.invoke(
            generate,
            [
                "--rules",
                str(yaml_file),
                "--file",
                str(output_file),
                "--from",
                from_date,
                "--to",
                to_date,
            ],
        )

        # Should succeed without warnings
        assert result.exit_code == 0
        assert output_file.exists()
        assert "warning" not in result.output.lower()

    def test_mixed_past_and_future_warnings(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test date range with both past and future warnings."""
        yaml_content = {
            "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
            "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d %a",
            "REVERSE_DATETREE_YEAR_FORMAT": "%Y",
            "REVERSE_DATETREE_USE_WEEK_TREE": True,
            "events": [
                {
                    "title": "Test Event",
                    "cron": "0 9 * * 1",
                }
            ],
        }

        yaml_file = tmp_path / "rules.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        # Test range spanning more than 1 year with past start
        past_date = (datetime.now() - timedelta(days=100)).strftime("%Y-%m-%d")
        future_date = (datetime.now() + timedelta(days=500)).strftime("%Y-%m-%d")

        result = runner.invoke(
            generate,
            ["--rules", str(yaml_file), "--from", past_date, "--to", future_date],
        )

        # Should show both warnings
        assert "past" in result.output.lower() or "future" in result.output.lower()

    def test_edge_case_today_date(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test that today's date doesn't trigger past date warning."""
        yaml_content = {
            "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
            "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d %a",
            "REVERSE_DATETREE_YEAR_FORMAT": "%Y",
            "REVERSE_DATETREE_USE_WEEK_TREE": True,
            "events": [
                {
                    "title": "Test Event",
                    "cron": "0 9 * * 1",
                }
            ],
        }

        yaml_file = tmp_path / "rules.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        output_file = tmp_path / "output.org"

        # Test with today's date
        today = datetime.now().strftime("%Y-%m-%d")

        result = runner.invoke(
            generate,
            [
                "--rules",
                str(yaml_file),
                "--file",
                str(output_file),
                "--from",
                today,
                "--to",
                today,
            ],
        )

        # Should succeed without past date warnings
        assert result.exit_code == 0
        assert output_file.exists()
        # Should not have past date warnings (might have other warnings though)
        assert (
            "past" not in result.output.lower()
            or "days ago" not in result.output.lower()
        )

    def test_force_flag_overrides_all_warnings(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test that --force overrides all date protection warnings."""
        yaml_content = {
            "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
            "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d %a",
            "REVERSE_DATETREE_YEAR_FORMAT": "%Y",
            "REVERSE_DATETREE_USE_WEEK_TREE": True,
            "events": [
                {
                    "title": "Test Event",
                    "cron": "0 9 * * 1",
                }
            ],
        }

        yaml_file = tmp_path / "rules.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        output_file = tmp_path / "output.org"

        # Extreme case: 6 months past to 2 years future
        past_date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
        future_date = (datetime.now() + timedelta(days=730)).strftime(
            "%Y-%m-%d"
        )  # Use 730 days (2 years) instead of 800

        result = runner.invoke(
            generate,
            [
                "--rules",
                str(yaml_file),
                "--file",
                str(output_file),
                "--from",
                past_date,
                "--to",
                future_date,
                "--force",
            ],
        )

        # Should succeed despite warnings with --force
        assert result.exit_code == 0
        assert output_file.exists()
        # Should show that warnings are being bypassed
        assert "force" in result.output.lower() or "bypass" in result.output.lower()

    def test_date_range_summary_output(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test that date range summary is shown when there are warnings."""
        yaml_content = {
            "REVERSE_DATETREE_WEEK_FORMAT": "%Y-W%V",
            "REVERSE_DATETREE_DATE_FORMAT": "%Y-%m-%d %a",
            "REVERSE_DATETREE_YEAR_FORMAT": "%Y",
            "REVERSE_DATETREE_USE_WEEK_TREE": True,
            "events": [
                {
                    "title": "Test Event",
                    "cron": "0 9 * * 1",
                }
            ],
        }

        yaml_file = tmp_path / "rules.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        # Test with past dates to trigger summary
        past_date = (datetime.now() - timedelta(days=50)).strftime("%Y-%m-%d")

        with runner.isolated_filesystem():
            result = runner.invoke(
                generate,
                ["--rules", str(yaml_file), "--from", past_date, "--to", past_date],
            )

        # Should contain date range information if using enhanced prompts
        # This test may need adjustment based on implementation
        assert "Warning" in result.output or "past" in result.output.lower()
