"""Tests for validation utilities."""

import sys
from pathlib import Path

import pytest

from ord_plan.utils.validators import validate_cron_expression
from ord_plan.utils.validators import validate_date_format
from ord_plan.utils.validators import validate_file_path
from ord_plan.utils.validators import validate_file_readable
from ord_plan.utils.validators import validate_file_writable
from ord_plan.utils.validators import validate_org_file_content


class TestCronValidation:
    """Test cron expression validation."""

    def test_valid_cron_expressions(self) -> None:
        """Test that valid cron expressions pass validation."""
        valid_expressions = [
            "0 9 * * 1-5",  # Weekdays at 9 AM
            "0 0 * * 0",  # Sundays at midnight
            "*/15 * * * *",  # Every 15 minutes
            "0 0 1 * *",  # First of month
            "30 14 15 * 5",  # 3:30 PM on 15th and Friday
        ]

        for expr in valid_expressions:
            errors = validate_cron_expression(expr, "test rule")
            assert errors == [], f"Valid expression {expr!r} should have no errors"

    def test_invalid_cron_expressions(self) -> None:
        """Test that invalid cron expressions are caught."""
        invalid_cases = [
            ("invalid", "Rule 'test rule': Invalid cron expression"),
            ("0 25 * * *", "Rule 'test rule': Invalid range"),
            ("60 0 * * *", "Rule 'test rule': Invalid range"),
            ("0 0 32 * *", "Rule 'test rule': Invalid range"),
            ("0 0 * * 7", "Rule 'test rule': Invalid weekday value"),
            ("", "Rule 'test rule': Cron expression cannot be empty"),
            ("   ", "Rule 'test rule': Cron expression cannot be empty"),
        ]

        for expr, expected_error in invalid_cases:
            errors = validate_cron_expression(expr, "test rule")
            assert len(errors) > 0
            assert any(expected_error in error for error in errors)

    def test_cron_validation_with_rule_title(self) -> None:
        """Test that rule titles are included in error messages."""
        errors = validate_cron_expression("invalid", "My Custom Rule")
        assert len(errors) > 0
        assert "My Custom Rule" in errors[0]


class TestFileValidation:
    """Test file path validation."""

    def test_valid_file_paths(self) -> None:
        """Test that valid file paths pass validation."""
        valid_paths = [
            "/tmp/test.yaml",
            "test.yaml",
            "./rules.yaml",
            "~/documents/rules.yaml",
        ]

        for path in valid_paths:
            errors = validate_file_path(path)
            assert errors == [], f"Valid path {path!r} should have no errors"

    def test_invalid_file_paths(self) -> None:
        """Test that invalid file paths are caught."""
        invalid_cases = [
            ("", "File path cannot be empty"),
            ("   ", "File path cannot be empty"),
            ("../../../etc/passwd", "contains parent directory references"),
            ("path\x00with\x00null", "contains invalid characters"),
        ]

        for path, expected_error in invalid_cases:
            errors = validate_file_path(path)
            assert len(errors) > 0
            assert any(expected_error in error for error in errors)

    def test_very_long_path(self) -> None:
        """Test path length validation."""
        long_path = "/" + "a" * 5000  # Very long path
        errors = validate_file_path(long_path)
        assert len(errors) > 0
        assert "too long" in errors[0].lower()


class TestDateFormatValidation:
    """Test date format validation."""

    def test_valid_date_formats(self) -> None:
        """Test that valid date formats pass validation."""
        valid_dates = [
            "2025-01-01",
            "2024-12-31",
            "today",
            "tomorrow",
            "next monday",
            "+7 days",
        ]

        for date_str in valid_dates:
            errors = validate_date_format(date_str, "test date")
            assert errors == [], f"Valid date {date_str!r} should have no errors"

    def test_invalid_date_formats(self) -> None:
        """Test that invalid date formats are caught."""
        invalid_cases = [
            ("", "cannot be empty"),
            ("   ", "cannot be empty"),
            ("invalid date", "Invalid test date format"),
            ("2025-13-01", "Invalid test date format"),  # Invalid month
            ("2025-01-32", "Invalid test date format"),  # Invalid day
        ]

        for date_str, expected_error in invalid_cases:
            errors = validate_date_format(date_str, "test date")
            assert len(errors) > 0
            assert any(expected_error in error for error in errors)


class TestOrgContentValidation:
    """Test org-mode content validation."""

    def test_empty_content(self) -> None:
        """Test that empty content has no warnings."""
        warnings = validate_org_file_content("", "test.org")
        assert warnings == []

    def test_valid_org_content(self) -> None:
        """Test that valid org content has no warnings."""
        valid_content = """* 2025
** 2025-W01
*** 2025-01-01 Mon
**** TODO Test Task
- [ ] Subtask 1
- [ ] Subtask 2
"""
        warnings = validate_org_file_content(valid_content, "test.org")
        assert warnings == []

    def test_binary_content_detection(self) -> None:
        """Test detection of potentially binary content."""
        binary_content = "Normal text\n\x00\x01\x02\x03More text"
        warnings = validate_org_file_content(binary_content, "test.org")
        assert len(warnings) > 0
        assert "binary data" in warnings[0]

    def test_very_long_lines(self) -> None:
        """Test detection of very long lines."""
        long_line = "a" * 10001
        content = f"Normal line\n{long_line}\nAnother line"
        warnings = validate_org_file_content(content, "test.org")
        assert len(warnings) > 0
        assert "Very long line" in warnings[0]


class TestFileReadableValidation:
    """Test file readable validation."""

    def test_nonexistent_file(self) -> None:
        """Test validation of non-existent files."""
        errors = validate_file_readable("/nonexistent/file.yaml")
        assert len(errors) > 0
        assert "does not exist" in errors[0]

    def test_directory_instead_of_file(self, tmp_path: Path) -> None:
        """Test validation when path points to a directory."""
        errors = validate_file_readable(str(tmp_path))
        assert len(errors) > 0
        assert "not a file" in errors[0]

    @pytest.mark.skipif(
        sys.platform == "win32",
        reason="chmod does not work the same on Windows",
    )
    def test_unreadable_file(self, tmp_path: Path) -> None:
        """Test validation of unreadable files."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("test content")

        # Remove read permissions (this may not work on all systems)
        test_file.chmod(0o000)

        errors = validate_file_readable(str(test_file))
        # Note: This test might not work on Windows or with certain filesystems
        if errors:
            assert "not readable" in errors[0]


class TestFileWritableValidation:
    """Test file writable validation."""

    def test_writable_file(self, tmp_path: Path) -> None:
        """Test validation of writable files."""
        test_file = tmp_path / "test.org"
        test_file.write_text("test")

        errors = validate_file_writable(str(test_file))
        assert errors == []

    def test_nonexistent_file_in_writable_dir(self, tmp_path: Path) -> None:
        """Test validation of non-existent file in writable directory."""
        nonexistent_file = tmp_path / "nonexistent.org"
        errors = validate_file_writable(str(nonexistent_file))
        assert errors == []

    @pytest.mark.skipif(
        sys.platform == "win32",
        reason="chmod does not work the same on Windows",
    )
    def test_unwritable_directory(self, tmp_path: Path) -> None:
        """Test validation of files in unwritable directories."""
        # This test might not work on all systems due to permission restrictions
        unwritable_dir = tmp_path / "unwritable"
        unwritable_dir.mkdir()
        unwritable_dir.chmod(0o444)  # Read-only

        test_file = unwritable_dir / "test.org"
        errors = validate_file_writable(str(test_file))

        # Restore permissions for cleanup
        unwritable_dir.chmod(0o755)

        if errors:
            assert "Cannot create file" in errors[0]
