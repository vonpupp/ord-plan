"""Tests for DateService."""

import pytest
from datetime import datetime, timedelta

from ord_plan.services.date_service import DateService


class TestDateService:
    """Test cases for DateService."""

    def test_parse_default_week_range(self) -> None:
        """Test default date range (current week)."""
        date_range = DateService.parse_date_range(None, None)

        # Should be Monday to Sunday of current week
        assert date_range.start_date.weekday() == 0  # Monday
        assert date_range.end_date.weekday() == 6  # Sunday
        assert date_range.start_date.hour == 0
        assert date_range.start_date.minute == 0
        assert date_range.end_date.hour == 23
        assert date_range.end_date.minute == 59

    def test_parse_absolute_dates(self) -> None:
        """Test parsing absolute date strings."""
        date_range = DateService.parse_date_range("2025-01-01", "2025-01-03")

        assert date_range.start_date.year == 2025
        assert date_range.start_date.month == 1
        assert date_range.start_date.day == 1
        assert date_range.end_date.year == 2025
        assert date_range.end_date.month == 1
        assert date_range.end_date.day == 3

    def test_parse_today(self) -> None:
        """Test parsing 'today'."""
        date_range = DateService.parse_date_range("today", "today")

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_today = datetime.now().replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

        assert date_range.start_date.date() == today.date()
        assert date_range.end_date.date() == end_today.date()

    def test_parse_tomorrow(self) -> None:
        """Test parsing 'tomorrow'."""
        date_range = DateService.parse_date_range("tomorrow", "tomorrow")

        tomorrow = datetime.now() + timedelta(days=1)
        assert date_range.start_date.date() == tomorrow.date()
        assert date_range.end_date.date() == tomorrow.date()
