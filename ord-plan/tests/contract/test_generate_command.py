"""CLI contract tests for ord-plan generate command."""

import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest
import yaml

from ord_plan.cli.generate import generate
from tests.fixtures import get_fixture_path, read_fixture


class TestGenerateCommandContract:
    """Test CLI interface compliance and parameter validation."""

    def test_required_rules_parameter(self, runner):
        """Test that --rules parameter is required."""
        result = runner.invoke(generate, [])

        assert result.exit_code != 0
        assert "Missing option" in result.output or "--rules" in result.output

    def test_rules_file_must_exist(self, runner):
        """Test that rules file must exist."""
        result = runner.invoke(generate, ["--rules", "/nonexistent/file.yaml"])

        assert result.exit_code != 0
        assert (
            "does not exist" in result.output or "File does not exist" in result.output
        )

    def test_rules_file_must_be_readable(self, runner, tmp_path):
        """Test that rules file must be readable."""
        unreadable_file = tmp_path / "unreadable.yaml"
        unreadable_file.write_text("test")
        unreadable_file.chmod(0o000)

        result = runner.invoke(generate, ["--rules", str(unreadable_file)])

        assert result.exit_code != 0
        assert "not readable" in result.output

    def test_optional_file_parameter(self, runner):
        """Test that --file parameter is optional."""
        # Use fixture file
        yaml_file = get_fixture_path("minimal_events.yaml")

        # Should work without --file (output to stdout)
        result = runner.invoke(
            generate,
            ["--rules", str(yaml_file), "--from", "2025-12-22", "--to", "2025-12-22"],
        )

        assert result.exit_code == 0
        # Should have some output to stdout
        assert result.output.strip() != ""

    def test_from_to_parameter_validation(self, runner, tmp_path):
        """Test --from and --to parameter validation."""
        yaml_content = {
            "events": [
                {
                    "title": "Test Event",
                    "cron": "0 9 * * 1",
                }
            ]
        }

        yaml_file = tmp_path / "rules.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        # Test invalid date format
        result = runner.invoke(
            generate, ["--rules", str(yaml_file), "--from", "invalid-date"]
        )

        assert result.exit_code != 0
        assert "Invalid" in result.output and "format" in result.output

    def test_force_flag_parameter(self, runner, tmp_path):
        """Test --force flag parameter."""
        yaml_content = {
            "events": [
                {
                    "title": "Test Event",
                    "cron": "0 9 * * 1",
                }
            ]
        }

        yaml_file = tmp_path / "rules.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        # Should work with --force flag
        result = runner.invoke(
            generate,
            [
                "--rules",
                str(yaml_file),
                "--from",
                "2024-01-01",  # Past date to trigger warnings
                "--force",
            ],
        )

        # Should succeed due to --force flag
        assert result.exit_code == 0

    def test_dry_run_flag_parameter(self, runner, tmp_path):
        """Test --dry-run flag parameter."""
        yaml_content = {
            "events": [
                {
                    "title": "Test Event",
                    "cron": "0 9 * * 1",
                }
            ]
        }

        yaml_file = tmp_path / "rules.yaml"
        output_file = tmp_path / "output.org"
        yaml_file.write_text(yaml.dump(yaml_content))

        # Should work with --dry-run flag
        result = runner.invoke(
            generate,
            ["--rules", str(yaml_file), "--file", str(output_file), "--dry-run"],
        )

        # Should not create file with --dry-run
        assert not output_file.exists()
        assert result.exit_code == 0

    def test_help_output_format(self, runner):
        """Test that help output includes required information."""
        result = runner.invoke(generate, ["--help"])

        assert result.exit_code == 0
        assert "--rules" in result.output
        assert "--file" in result.output
        assert "--from" in result.output
        assert "--to" in result.output
        assert "--force" in result.output
        assert "Examples:" in result.output
        assert "Date Formats:" in result.output

    def test_exit_codes(self, runner):
        """Test various exit code scenarios."""
        # Use fixture file
        yaml_file = get_fixture_path("minimal_events.yaml")

        # Test exit code 0 (success)
        result = runner.invoke(
            generate,
            ["--rules", str(yaml_file), "--from", "2025-12-22", "--to", "2025-12-22"],
        )
        assert result.exit_code == 0

        # Test exit code 2 (invalid input - Click usage error)
        result = runner.invoke(generate, ["--rules", "nonexistent.yaml"])
        assert result.exit_code == 2

    def test_parameter_combinations(self, runner, tmp_path):
        """Test various parameter combinations."""
        # Use fixture file
        yaml_file = get_fixture_path("minimal_events.yaml")
        output_file = tmp_path / "output.org"

        # Test --from and --to combination
        result = runner.invoke(
            generate,
            [
                "--rules",
                str(yaml_file),
                "--file",
                str(output_file),
                "--from",
                "2025-12-22",  # Monday
                "--to",
                "2025-12-22",  # Same day
            ],
        )
        assert result.exit_code == 0

        # Test --to without --from (should use today)
        result = runner.invoke(
            generate,
            [
                "--rules",
                str(yaml_file),
                "--file",
                str(output_file),
                "--to",
                "2025-12-31",
            ],
        )
        assert result.exit_code == 0

    def test_output_format_consistency(self, runner, tmp_path):
        """Test that output format is consistent org-mode."""
        yaml_content = {
            "events": [
                {
                    "title": "Test Event",
                    "cron": "0 9 * * 1",
                    "todo_state": "TODO",
                    "tags": ["test"],
                }
            ]
        }

        yaml_file = tmp_path / "rules.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        result = runner.invoke(
            generate,
            [
                "--rules",
                str(yaml_file),
                "--from",
                "2025-12-22",  # Monday
                "--to",
                "2025-12-22",  # Same day
            ],
        )

        assert result.exit_code == 0

        # Check for org-mode format indicators
        output_lines = result.output.split("\n")
        header_lines = [line for line in output_lines if line.startswith("*")]

        # Should have org-mode headers
        assert len(header_lines) > 0
        assert any("TODO" in line for line in output_lines)
        assert any(":test:" in line for line in output_lines)

    def test_error_message_quality(self, runner, tmp_path):
        """Test that error messages are helpful and specific."""
        # Test YAML syntax error
        invalid_yaml = tmp_path / "invalid.yaml"
        invalid_yaml.write_text(
            "events:\n  - title: Test\n  cron: invalid cron  # Missing required structure"
        )

        result = runner.invoke(generate, ["--rules", str(invalid_yaml)])

        assert result.exit_code != 0
        # Should provide specific error information
        assert len(result.output) > 20  # Detailed error message

    def test_parameter_order_independence(self, runner, tmp_path):
        """Test that parameter order doesn't matter."""
        yaml_content = {
            "events": [
                {
                    "title": "Test Event",
                    "cron": "0 9 * * 1",
                }
            ]
        }

        yaml_file = tmp_path / "rules.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))
        output_file = tmp_path / "output.org"

        # Test different parameter orders
        orders = [
            [
                "--rules",
                str(yaml_file),
                "--file",
                str(output_file),
                "--from",
                "2025-12-22",
                "--to",
                "2025-12-22",
            ],
            [
                "--from",
                "2025-12-22",
                "--to",
                "2025-12-22",
                "--rules",
                str(yaml_file),
                "--file",
                str(output_file),
            ],
            [
                "--file",
                str(output_file),
                "--from",
                "2025-12-22",
                "--to",
                "2025-12-22",
                "--rules",
                str(yaml_file),
            ],
        ]

        for order in orders:
            result = runner.invoke(generate, order)
            assert result.exit_code == 0

    def test_long_parameter_values(self, runner):
        """Test handling of long parameter values."""
        # Use fixture file with long content
        yaml_file = get_fixture_path("test_rules_long_content.yaml")

        result = runner.invoke(
            generate,
            [
                "--rules",
                str(yaml_file),
                "--from",
                "2025-12-24",
                "--to",
                "2025-12-24",  # Wednesday for long content test
            ],
        )

        # Should handle long values gracefully
        assert result.exit_code == 0
        assert len(result.output) > 500  # Should contain long content

    def test_unicode_support(self, runner):
        """Test Unicode character support."""
        # Use fixture file with unicode content
        yaml_file = get_fixture_path("test_events.yaml")

        result = runner.invoke(
            generate,
            [
                "--rules",
                str(yaml_file),
                "--from",
                "2025-12-23",
                "--to",
                "2025-12-23",  # Tuesday for unicode test
            ],
        )

        # Should handle Unicode without errors
        assert result.exit_code == 0
        assert "ñáéíóú" in result.output
        assert "中文" in result.output or "français" in result.output
