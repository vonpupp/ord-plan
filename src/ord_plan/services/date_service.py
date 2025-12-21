"""Date service for handling date ranges and validation."""

from datetime import datetime
from datetime import timedelta
from typing import List
from typing import Tuple
from typing import Union

import click
from dateutil import parser as date_parser

from ..models.date_range import DateRange


class DateService:
    """Service for date range processing and validation."""

    @staticmethod
    def parse_date_range(
        from_str: Union[str, None], to_str: Union[str, None]
    ) -> DateRange:
        """Parse date range from input strings.

        Args:
            from_str: Start date string (YYYY-MM-DD or relative)
            to_str: End date string (YYYY-MM-DD or relative)

        Returns:
            DateRange object
        """
        # Default to this week (Monday to Sunday) if no dates provided
        if from_str is None and to_str is None:
            from_date, to_date = DateService._get_default_week_range()
        else:
            from_date = (
                DateService._parse_single_date(from_str) if from_str else datetime.now()
            )
            to_date = DateService._parse_single_date(to_str) if to_str else from_date

        # Ensure from_date is at start of day and to_date is at end of day
        from_date = from_date.replace(hour=0, minute=0, second=0, microsecond=0)
        to_date = to_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        return DateRange(start_date=from_date, end_date=to_date)

    @staticmethod
    def _get_default_week_range() -> Tuple[datetime, datetime]:
        """Get default date range (current Monday to Sunday)."""
        now = datetime.now()

        # Find Monday of current week
        days_since_monday = now.weekday()  # Monday is 0, Sunday is 6
        monday = now - timedelta(days=days_since_monday)

        # Find Sunday of current week
        days_until_sunday = 6 - days_since_monday
        sunday = now + timedelta(days=days_until_sunday)

        return monday, sunday

    @staticmethod
    def _parse_single_date(date_str: str) -> datetime:
        """Parse a single date string.

        Args:
            date_str: Date string (YYYY-MM-DD or relative like "today", "next monday")

        Returns:
            datetime object

        Raises:
            ValueError: If date string is empty
            BadParameter: If date string cannot be parsed
        """
        if not date_str:
            return datetime.now()

        # Handle common relative dates
        date_str_lower = date_str.lower()

        if date_str_lower == "today":
            return datetime.now()
        elif date_str_lower == "tomorrow":
            return datetime.now() + timedelta(days=1)
        elif date_str_lower == "yesterday":
            return datetime.now() - timedelta(days=1)
        elif date_str_lower.startswith("next"):
            # Handle "next monday", "next week", etc.
            remaining = date_str_lower[5:].strip()  # Remove "next "
            now = datetime.now()

            if remaining == "week":
                # Next Monday to Sunday
                days_until_next_monday = (7 - now.weekday()) % 7 or 7
                next_monday = now + timedelta(days=days_until_next_monday)
                return next_monday
            elif remaining == "month":
                # First day of next month
                if now.month == 12:
                    return datetime(now.year + 1, 1, 1)
                else:
                    return datetime(now.year, now.month + 1, 1)
            elif remaining == "year":
                # First day of next year
                return datetime(now.year + 1, 1, 1)
            elif remaining in ["monday", "mon"]:
                # Next Monday
                days_until_monday = (7 - now.weekday()) % 7 or 7
                return now + timedelta(days=days_until_monday)
            elif remaining in ["tuesday", "tue"]:
                # Next Tuesday
                days_until_tuesday = (8 - now.weekday()) % 7 or 7
                return now + timedelta(days=days_until_tuesday)
            elif remaining in ["wednesday", "wed"]:
                # Next Wednesday
                days_until_wednesday = (9 - now.weekday()) % 7 or 7
                return now + timedelta(days=days_until_wednesday)
            elif remaining in ["thursday", "thu"]:
                # Next Thursday
                days_until_thursday = (10 - now.weekday()) % 7 or 7
                return now + timedelta(days=days_until_thursday)
            elif remaining in ["friday", "fri"]:
                # Next Friday
                days_until_friday = (11 - now.weekday()) % 7 or 7
                return now + timedelta(days=days_until_friday)
            elif remaining in ["saturday", "sat"]:
                # Next Saturday
                days_until_saturday = (12 - now.weekday()) % 7 or 7
                return now + timedelta(days=days_until_saturday)
            elif remaining in ["sunday", "sun"]:
                # Next Sunday
                days_until_sunday = (13 - now.weekday()) % 7 or 7
                return now + timedelta(days=days_until_sunday)

        # Handle "+N days" format
        if date_str.startswith("+") and "days" in date_str_lower:
            try:
                days_str = date_str_lower.split()[1]
                days = int(days_str)
                return datetime.now() + timedelta(days=days)
            except (ValueError, IndexError) as e:
                raise click.BadParameter(
                    f"Invalid days format: {date_str}. "
                    "Use '+N days' where N is a number"
                ) from e

        # Try to parse as absolute date or using dateutil parser
        try:
            result: datetime = date_parser.parse(date_str)

            # Ensure the result is a datetime object
            if not isinstance(result, datetime):
                raise ValueError(
                    f"Date parser returned non-datetime object: {type(result)}"
                )

            return result
        except Exception:
            # Fallback to manual parsing for YYYY-MM-DD format
            try:
                # Try to parse as YYYY-MM-DD format
                parts = date_str.split("-")
                if len(parts) == 3:
                    year, month, day = map(int, parts)
                    # Handle leap year validation
                    try:
                        return datetime(year, month, day)
                    except ValueError as ve:
                        # If it's a leap year issue, try the 28th
                        if "day is out of range" in str(ve) and month == 2:
                            return datetime(year, month, 28)
                        # For other errors, try the last day of the month
                        import calendar

                        last_day = calendar.monthrange(year, month)[1]
                        return datetime(year, month, last_day)
                else:
                    raise ValueError(f"Invalid date format: {date_str}")
            except Exception as fallback_error:
                raise click.BadParameter(
                    f"Unable to parse date: {date_str}. Error: {fallback_error}"
                ) from fallback_error

    @staticmethod
    def validate_date_range(date_range: DateRange, force: bool = False) -> bool:
        """Validate date range and handle warnings.

        Args:
            date_range: DateRange to validate
            force: Whether to bypass warnings

        Returns:
            True if valid and should proceed, False if user cancelled
        """
        # Check for critical date protection issues
        if not force:
            # Enhanced past date warnings with context
            if date_range.has_past_dates():
                days_past = (
                    datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    - date_range.start_date
                ).days

                if days_past > 90:  # More than 3 months in past
                    click.echo(
                        f"⚠️  Warning: You're generating events for dates "
                        f"{days_past} days in the past.",
                        err=True,
                    )
                    click.echo(
                        "   This might not be what you intended. "
                        "Use --force to override.",
                        err=True,
                    )
                    if not click.confirm("   Do you want to continue anyway?"):
                        return False
                elif days_past > 30:  # More than 1 month in past
                    click.echo(
                        f"⚠️  Warning: Generating events for dates "
                        f"{days_past} days in the past.",
                        err=True,
                    )
                    click.echo("   Consider if this is intentional.", err=True)
                    if not click.confirm("   Do you want to continue?"):
                        return False
                else:
                    click.echo(
                        f"⚠️  Warning: Generating events for past dates "
                        f"({days_past} days ago).",
                        err=True,
                    )
                    if not click.confirm("   Do you want to continue?"):
                        return False

            # Enhanced future date warnings
            if date_range.has_distant_future_dates():
                years_future = date_range.end_date.year - datetime.now().year

                if years_future > 1:
                    click.echo(
                        f"⚠️  Warning: You're generating events more than "
                        f"{years_future} years in the future.",
                        err=True,
                    )
                    click.echo(
                        "   This might not be what you intended. "
                        "Use --force to override.",
                        err=True,
                    )
                    if not click.confirm("   Do you want to continue anyway?"):
                        return False

        # Handle standard warnings with enhanced formatting
        if date_range.warnings and not force:
            click.echo("⚠️  Additional warnings:", err=True)
            for warning in date_range.warnings:
                click.echo(f"   - {warning}", err=True)

            if not click.confirm("   Do you want to proceed despite these warnings?"):
                return False
        elif force and date_range.warnings:
            # Show warnings even when forcing so user knows what was bypassed
            click.echo(
                "ℹ️  Note: Bypassing the following warnings with --force:", err=True
            )
            for warning in date_range.warnings:
                click.echo(f"   - {warning}", err=True)

        return True

    @staticmethod
    def prompt_user_confirmation(message: str, default: bool = False) -> bool:
        """Enhanced user confirmation with better defaults.

        Args:
            message: Confirmation message to display
            default: Default value if user just presses Enter

        Returns:
            True if user confirms, False otherwise
        """
        return click.confirm(message, default=default)

    @staticmethod
    def confirm_date_range(date_range: DateRange) -> bool:
        """Ask user to confirm date range before proceeding.

        Args:
            date_range: Date range to confirm

        Returns:
            True if user confirms, False otherwise
        """
        from_date_str = date_range.start_date.strftime("%Y-%m-%d")
        to_date_str = date_range.end_date.strftime("%Y-%m-%d")
        days_count = (
            date_range.end_date.date() - date_range.start_date.date()
        ).days + 1

        click.echo("\n📅 Date Range Summary:")
        click.echo(f"   From: {from_date_str}")
        click.echo(f"   To:   {to_date_str}")
        click.echo(f"   Days: {days_count}")

        if date_range.warnings:
            click.echo(f"   Warnings: {len(date_range.warnings)} issue(s) detected")

        return DateService.prompt_user_confirmation(
            "   Do you want to proceed with event generation?", default=True
        )

    @staticmethod
    def check_date_protection_violations(date_range: DateRange) -> List[str]:
        """Check for date protection violations without user interaction.

        Args:
            date_range: DateRange to check

        Returns:
            List of protection violation messages
        """
        violations = []

        if date_range.has_past_dates():
            days_past = (
                datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                - date_range.start_date
            ).days

            if days_past > 90:
                violations.append(
                    f"Generating events for dates {days_past} days in the past "
                    f"(more than 3 months)"
                )
            elif days_past > 30:
                violations.append(
                    f"Generating events for dates {days_past} days in the past "
                    f"(more than 1 month)"
                )

        if date_range.has_distant_future_dates():
            years_future = date_range.end_date.year - datetime.now().year
            if years_future > 1:
                violations.append(
                    f"Generating events {years_future} years in the future "
                    f"(beyond 1 year limit)"
                )

        return violations
