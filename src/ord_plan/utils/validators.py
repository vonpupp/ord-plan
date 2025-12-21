"""Validation utilities for ord-plan."""

import os
from typing import List

from croniter import croniter


HAS_DATEUTIL = True
try:
    from dateutil.parser import parse as _dateutil_parse
except ImportError:
    _dateutil_parse = None  # type: ignore[assignment]
    HAS_DATEUTIL = False


def validate_file_readable(file_path: str) -> List[str]:
    """Validate that a file exists and is readable."""
    errors = []

    if not os.path.exists(file_path):
        errors.append(f"File does not exist: {file_path}")
    elif not os.path.isfile(file_path):
        errors.append(f"Path is not a file: {file_path}")
    elif not os.access(file_path, os.R_OK):
        errors.append(f"File is not readable: {file_path}")

    return errors


def validate_file_writable(file_path: str) -> List[str]:
    """Validate that a file can be written to."""
    errors = []

    if os.path.exists(file_path):
        if not os.path.isfile(file_path):
            errors.append(f"Path exists but is not a file: {file_path}")
        elif not os.access(file_path, os.W_OK):
            errors.append(f"File is not writable: {file_path}")
    else:
        # Check if parent directory is writable for file creation
        directory = os.path.dirname(file_path)
        if directory:
            # Find first existing parent directory to check writability
            check_dir = directory
            while check_dir and not os.path.exists(check_dir):
                check_dir = os.path.dirname(check_dir)

            if check_dir and not os.access(check_dir, os.W_OK):
                errors.append(f"Cannot create file in directory: {directory}")

    return errors


def validate_cron_expression(
    cron_expr: str, rule_title: str = "unnamed rule"
) -> List[str]:
    """Validate cron expression with clear error messages.

    Args:
        cron_expr: The cron expression to validate
        rule_title: Title of rule for error context

    Returns:
        List of error messages, empty if valid
    """
    errors = []

    if not cron_expr or not cron_expr.strip():
        errors.append(f"Rule {rule_title!r}: Cron expression cannot be empty")
        return errors

    # Basic format validation first
    fields = cron_expr.strip().split()
    if len(fields) != 5:
        errors.append(
            f"Rule {rule_title!r}: Invalid cron expression {cron_expr!r}. "
            "Expected format: 'minute hour day month weekday' (5 fields required)"
        )
        return errors

    # Test if croniter can parse expression
    try:
        cron = croniter(cron_expr)
        # Test with a dummy date to catch more validation errors
        from datetime import datetime

        cron.get_next(datetime)
    except (ValueError, KeyError, OverflowError) as e:
        # Provide more user-friendly error messages
        error_msg = str(e).lower()

        if "invalid" in error_msg and "cron expression" in error_msg:
            errors.append(
                f"Rule {rule_title!r}: Invalid cron expression {cron_expr!r}. "
                "Expected format: 'minute hour day month weekday' (0-6 for weekdays)"
            )
        elif "field" in error_msg:
            errors.append(
                f"Rule {rule_title!r}: Invalid field in cron expression {cron_expr!r}. "
                "Check that all fields are within valid ranges: minute (0-59), "
                "hour (0-23), day (1-31), month (1-12), weekday (0-6)"
            )
        elif "range" in error_msg:
            errors.append(
                f"Rule {rule_title!r}: Invalid range in cron expression {cron_expr!r}. "
                "Ranges should be in format 'start-end' with valid values"
            )
        elif "step" in error_msg or "increment" in error_msg:
            errors.append(
                f"Rule {rule_title!r}: Invalid step value in cron expression "
                f"{cron_expr!r}\nStep values should be positive integers "
                "in format 'field/step'"
            )
        elif "weekday" in error_msg or "day of week" in error_msg:
            errors.append(
                f"Rule {rule_title!r}: Invalid weekday in cron expression "
                f"{cron_expr!r}\nWeekday should be 0-6 (Sunday=0) "
                "or use standard cron abbreviations"
            )
        else:
            errors.append(
                f"Rule {rule_title!r}: Invalid cron expression {cron_expr!r}: {e}. "
                "Please check your cron syntax"
            )
    except Exception as e:
        errors.append(
            f"Rule {rule_title!r}: Unexpected error validating cron expression "
            f"'{cron_expr}\\n!r': {e}"
        )

    # Additional validation for common mistakes
    if not errors:
        minute, hour, day, month, weekday = fields

        # Check for obviously invalid values
        if minute.isdigit() and (int(minute) < 0 or int(minute) > 59):
            errors.append(
                f"Rule {rule_title!r}: Invalid minute value {minute!r} (must be 0-59)"
            )

        if hour.isdigit() and (int(hour) < 0 or int(hour) > 23):
            errors.append(
                f"Rule {rule_title!r}: Invalid hour value {hour!r} (must be 0-23)"
            )

        if day.isdigit() and (int(day) < 1 or int(day) > 31):
            errors.append(
                f"Rule {rule_title!r}: Invalid day value {day!r} (must be 1-31)"
            )

        if month.isdigit() and (int(month) < 1 or int(month) > 12):
            errors.append(
                f"Rule {rule_title!r}: Invalid month value {month!r} (must be 1-12)"
            )

        if weekday.isdigit() and (int(weekday) < 0 or int(weekday) > 6):
            errors.append(
                f"Rule {rule_title!r}: Invalid weekday value {weekday!r} "
                f"(must be 0-6, Sunday=0)"
            )

    return errors


def validate_file_path(file_path: str) -> List[str]:
    """Validate file path format and basic constraints.

    Args:
        file_path: The file path to validate

    Returns:
        List of error messages, empty if valid
    """
    errors = []

    if not file_path or not file_path.strip():
        errors.append("File path cannot be empty")
        return errors

    # Check for potentially dangerous paths
    if ".." in file_path:
        errors.append(f"File path {file_path!r} contains parent directory references")

    # Check for null bytes
    if "\x00" in file_path:
        errors.append(f"File path {file_path!r} contains invalid characters")

    # Check path length (reasonable limits)
    if len(file_path) > 4096:  # Typical MAX_PATH limit
        errors.append("File path too long (max 4096 characters)")

    return errors


def validate_org_file_content(
    file_content: str, file_path: str = "unknown"
) -> List[str]:
    """Validate that file content is reasonable org-mode format (best effort).

    Args:
        file_content: Content to validate
        file_path: File path for error context

    Returns:
        List of warning messages (not errors since this is best effort)
    """
    warnings: List[str] = []

    if not file_content:
        # Empty file is fine, no warnings
        return warnings

    lines = file_content.split("\n")

    # Check for obviously non-org content patterns
    for i, line in enumerate(lines[:50]):  # Only check first 50 lines for performance
        line_stripped = line.strip()

        # Skip empty lines and comments
        if not line_stripped or line_stripped.startswith("#"):
            continue

        # Check for binary content indicators
        if any(char in line for char in ["\x00", "\x01", "\x02", "\x03", "\x04"]):
            warnings.append(
                f"{file_path}:{i + 1} - Warning: File appears to contain binary data"
            )
            break

        # Very long lines might indicate non-text content
        if len(line) > 10000:
            warnings.append(
                f"{file_path}:{i + 1} - Warning: Very long line detected, "
                "may not be text content"
            )

    return warnings


def validate_date_format(date_str: str, field_name: str = "date") -> List[str]:
    """Validate date string format for CLI input.

    Args:
        date_str: Date string to validate
        field_name: Name of the field for error context

    Returns:
        List of error messages, empty if valid
    """
    errors = []

    if not date_str or not date_str.strip():
        errors.append(f"{field_name} cannot be empty")
        return errors

    from datetime import datetime

    # Try YYYY-MM-DD format first (preferred)
    if len(date_str) == 10 and date_str[4] == "-" and date_str[7] == "-":
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return errors  # Valid date
        except ValueError:
            errors.append(
                f"Invalid {field_name} format: {date_str!r}. "
                "Use YYYY-MM-DD format or basic relative dates like "
                "'today', 'next monday'"
            )
            return errors

    # Try parsing with dateutil if available
    if HAS_DATEUTIL and _dateutil_parse is not None:
        try:
            _dateutil_parse(date_str)
            return errors  # Valid date
        except Exception:
            pass  # Fall through to basic validation

    # Basic relative date handling without dateutil
    lower_date = date_str.lower()
    if lower_date in ["today", "tomorrow", "yesterday"]:
        # These are valid basic relative dates
        return errors
    elif lower_date.startswith("next "):
        # Basic validation for "next day" format
        day_name = lower_date[5:]
        valid_days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        if day_name not in valid_days:
            errors.append(
                f"Invalid {field_name} format: {date_str!r}. "
                "Use YYYY-MM-DD format or basic relative dates like 'today', "
                "'next monday'"
            )
    elif lower_date.startswith("+") and "day" in lower_date:
        # Basic validation for "+N days" format
        try:
            days_part = lower_date.split()[0]
            int(days_part[1:])  # Should be parseable as int
        except (ValueError, IndexError):
            errors.append(
                f"Invalid {field_name} format: {date_str!r}. "
                "Use YYYY-MM-DD format or basic relative dates like 'today', "
                "'next monday'"
            )
    else:
        errors.append(
            f"Invalid {field_name} format: {date_str!r}. "
            "Use YYYY-MM-DD format or basic relative dates like 'today', 'next monday'"
        )

    return errors
