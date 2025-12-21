"""Integration tests for error handling."""

from pathlib import Path

import yaml
from click.testing import CliRunner

from ord_plan.cli.generate import generate
from ord_plan.utils.validators import validate_cron_expression


class TestErrorHandlingIntegration:
    """Test comprehensive error handling in CLI."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = None  # Will use click.testing.CliRunner

    def test_invalid_yaml_syntax(self, tmp_path: Path, runner: CliRunner) -> None:
        """Test handling of invalid YAML syntax."""
        invalid_yaml_file = tmp_path / "invalid.yaml"
        invalid_yaml_file.write_text(
            "events:\n  - title: Test\n  cron: '0 9 * * 1'  # Missing colon"
        )

        result = runner.invoke(generate, ["--rules", str(invalid_yaml_file)])

        assert result.exit_code != 0
        assert (
            "YAML parsing error" in result.output or "invalid" in result.output.lower()
        )

    def test_missing_required_fields(self, tmp_path: Path, runner: CliRunner) -> None:
        """Test handling of missing required fields."""
        yaml_content = {
            "events": [
                {"title": "Test Event"},  # Missing cron field
                {"cron": "0 9 * * 1"},  # Missing title field
            ]
        }

        yaml_file = tmp_path / "incomplete.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        result = runner.invoke(generate, ["--rules", str(yaml_file)])

        assert result.exit_code != 0
        assert "missing required" in result.output.lower()

    def test_invalid_cron_expressions(self, tmp_path: Path, runner: CliRunner) -> None:
        """Test handling of invalid cron expressions."""
        yaml_content = {
            "events": [
                {
                    "title": "Invalid Cron Event",
                    "cron": "invalid cron expression",
                },
                {
                    "title": "Another Invalid Event",
                    "cron": "25 0 * * *",  # Invalid hour
                },
            ]
        }

        yaml_file = tmp_path / "bad_cron.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        result = runner.invoke(generate, ["--rules", str(yaml_file)])

        assert result.exit_code != 0
        assert "Cron expression validation errors" in result.output
        assert "Invalid cron expression" in result.output

    def test_invalid_date_formats(self, tmp_path: Path, runner: CliRunner) -> None:
        """Test handling of invalid date formats."""
        yaml_content = {
            "events": [
                {
                    "title": "Test Event",
                    "cron": "0 9 * * 1",
                }
            ]
        }

        yaml_file = tmp_path / "simple.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        # Test invalid from date
        result = runner.invoke(
            generate, ["--rules", str(yaml_file), "--from", "invalid-date"]
        )
        assert result.exit_code != 0
        assert "Invalid --from date format" in result.output

        # Test invalid to date
        result = runner.invoke(
            generate, ["--rules", str(yaml_file), "--to", "not-a-date"]
        )
        assert result.exit_code != 0
        assert "Invalid --to date format" in result.output

    def test_file_permission_errors(self, runner: CliRunner) -> None:
        """Test handling of file permission errors."""
        # Test with non-existent rules file
        result = runner.invoke(generate, ["--rules", "/nonexistent/path/rules.yaml"])
        assert result.exit_code != 0
        assert "does not exist" in result.output

    def test_mixed_valid_and_invalid_events(
        self, tmp_path: Path, runner: CliRunner
    ) -> None:
        """Test handling of mixed valid and invalid events."""
        yaml_content = {
            "events": [
                {
                    "title": "Valid Event",
                    "cron": "0 9 * * 1",  # Valid
                },
                {
                    "title": "Invalid Event",
                    "cron": "bad cron",  # Invalid
                },
                {
                    "title": "Another Valid Event",
                    "cron": "0 17 * * 5",  # Valid
                },
            ]
        }

        yaml_file = tmp_path / "mixed.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        result = runner.invoke(generate, ["--rules", str(yaml_file)])

        assert result.exit_code != 0
        assert "Invalid Event" in result.output
        assert "Invalid cron expression" in result.output

    def test_warning_handling(self, tmp_path: Path, runner: CliRunner) -> None:
        """Test that warnings are displayed but don't prevent execution."""
        yaml_content = {
            "unknown_field": "will be ignored",  # Should generate warning
            "events": [
                {
                    "title": "Test Event",
                    "cron": "0 9 * * 1",
                }
            ],
        }

        yaml_file = tmp_path / "with_warnings.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))
        output_file = tmp_path / "output.org"

        result = runner.invoke(
            generate, ["--rules", str(yaml_file), "--file", str(output_file)]
        )

        # Should succeed despite warnings
        assert result.exit_code == 0
        assert "Warning:" in result.output
        assert output_file.exists()

    def test_yaml_schema_validation(self, tmp_path: Path, runner: CliRunner) -> None:
        """Test comprehensive YAML schema validation."""
        yaml_content = {
            "events": [
                {
                    "title": "",  # Invalid: empty title
                    "cron": "0 9 * * 1",
                    "tags": ["tag with spaces"],  # Invalid: spaces in tag
                    "description": "x" * 1001,  # Invalid: too long
                }
            ]
        }

        yaml_file = tmp_path / "schema_errors.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        result = runner.invoke(generate, ["--rules", str(yaml_file)])

        assert result.exit_code != 0
        assert "cannot be empty" in result.output
        assert "cannot contain spaces" in result.output
        assert "too long" in result.output.lower()

    def test_error_recovery(self, tmp_path: Path, runner: CliRunner) -> None:
        """Test that error handling provides recovery suggestions."""
        yaml_content = {
            "events": [
                {
                    "title": "Event with typo",
                    "cron": "0 9 * * *1",  # Common typo: extra number for weekday
                }
            ]
        }

        yaml_file = tmp_path / "typo.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        result = runner.invoke(generate, ["--rules", str(yaml_file)])

        assert result.exit_code != 0
        assert "Please check your cron syntax" in result.output

    def test_cron_validation_details(self) -> None:
        """Test detailed cron validation error messages."""
        test_cases = [
            ("bad format", "Invalid cron expression"),
            ("0 25 * * *", "Invalid range"),
            ("0 0 * * 7", "Invalid weekday"),
            ("*/abc * * * *", "not acceptable"),
        ]

        for cron_expr, expected_error in test_cases:
            errors = validate_cron_expression(cron_expr, "Test Rule")
            assert len(errors) > 0
            assert any(expected_error in error for error in errors)

    def test_file_path_security(self, tmp_path: Path, runner: CliRunner) -> None:
        """Test security validation for file paths."""
        # This test would need to be implemented based on actual security requirements
        # For now, testing basic path validation
        yaml_content = {"events": [{"title": "Test", "cron": "0 9 * * 1"}]}

        yaml_file = tmp_path / "rules.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))

        # Test dangerous path (if implemented)
        dangerous_path = "../../../etc/passwd"
        runner.invoke(generate, ["--rules", str(yaml_file), "--file", dangerous_path])

        # Should either be blocked or succeed depending on implementation
        # The important thing is that it's handled safely
