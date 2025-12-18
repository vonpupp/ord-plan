"""Contract tests for ord-plan generate command."""

from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from ord_plan.cli.generate import generate
from tests.fixtures import get_fixture_path


class TestGenerateCommandContract:
    """Test CLI interface compliance and parameter validation."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Fixture for invoking command-line interfaces."""
        return CliRunner()

    def test_required_rules_parameter(self, runner: CliRunner) -> None:
        """Test that --rules parameter is required."""
        result = runner.invoke(generate, [])

        assert result.exit_code != 0
        assert "Missing option" in result.output or "--rules" in result.output

    def test_rules_file_must_exist(self, runner: CliRunner) -> None:
        """Test that rules file must exist."""
        result = runner.invoke(generate, ["--rules", "/nonexistent/file.yaml"])

        assert result.exit_code != 0
        assert (
            "does not exist" in result.output or "File does not exist" in result.output
        )

    def test_rules_file_must_be_readable(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test that rules file must be readable."""
        unreadable_file = tmp_path / "unreadable.yaml"
        unreadable_file.write_text("test")

        # Try to make file unreadable - this might not work on all systems
        try:
            unreadable_file.chmod(0o000)
        except (OSError, PermissionError):
            pytest.skip("File permission test not supported on this platform")
            return

        result = runner.invoke(generate, ["--rules", str(unreadable_file)])

        assert result.exit_code != 0
        assert (
            "not readable" in result.output
            or "YAML validation errors" in result.output
            or "YAML parsing error" in result.output
        )

    def test_optional_file_parameter(self, runner: CliRunner) -> None:
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

    def test_from_to_parameter_validation(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
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
            generate,
            ["--rules", str(yaml_file), "--from", "invalid-date"],
        )

        assert result.exit_code != 0
        assert "Invalid --from date format" in result.output

    def test_force_flag_parameter(self, runner: CliRunner, tmp_path: Path) -> None:
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

    def test_dry_run_flag_parameter(self, runner: CliRunner, tmp_path: Path) -> None:
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
        yaml_file.write_text(yaml.dump(yaml_content))

        # Should work with --dry-run flag
        result = runner.invoke(
            generate,
            [
                "--rules",
                str(yaml_file),
                "--from",
                "2025-12-22",
                "--to",
                "2025-12-22",
                "--dry-run",
            ],
        )
        assert result.exit_code == 0
        assert "DRY RUN" in result.output

    def test_help_output_format(self, runner: CliRunner) -> None:
        """Test that help output includes required information."""
        result = runner.invoke(generate, ["--help"])

        assert result.exit_code == 0
        # Should include usage information
        assert "Usage:" in result.output
        assert "--rules" in result.output
        assert "--file" in result.output
        assert "--from" in result.output
        assert "--to" in result.output

    def test_exit_codes(self, runner: CliRunner) -> None:
        """Test various exit code scenarios."""
        # Use fixture file
        yaml_file = get_fixture_path("minimal_events.yaml")

        # Test exit code 0 (success)
        result = runner.invoke(
            generate,
            ["--rules", str(yaml_file), "--from", "2025-12-22"],
        )

        assert result.exit_code == 0

        # Test exit code 1 (invalid input)
        result = runner.invoke(
            generate, ["--rules", str(yaml_file), "--from", "nonexistent.yaml"]
        )

        assert result.exit_code == 1
        assert "Invalid" in result.output

    def test_parameter_combinations(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test various parameter combinations."""
        # Create YAML with long title
        yaml_content = {
            "events": [
                {
                    "title": "This is a very long description that contains many characters to test.",
                    "cron": "0 9 * * 1",
                }
            ]
        }

        yaml_file = tmp_path / "rules.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        result = runner.invoke(
            generate,
            [
                "--dry-run",
                "--from",
                "2025-12-22",
                "--to",
                "2025-12-22",
                "--rules",
                str(yaml_file),
            ],
        )

        assert result.exit_code == 0
        # Test parameter order independence
        assert len(result.output.strip()) > 0  # Should have some output

    def test_long_parameter_values(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test handling of long parameter values."""
        # Use fixture file with long content
        yaml_content = {
            "events": [
                {
                    "title": "This is a very long description that contains many characters to test.",
                    "cron": "0 9 * * 1",
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
                "2025-12-22",
                "--to",
                "2025-12-22",
            ],
        )

        assert result.exit_code == 0
        # Should handle long values gracefully
        assert len(result.output) > 0
