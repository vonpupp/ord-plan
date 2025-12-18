"""Tests for date protection functionality."""

from datetime import datetime
from datetime import timedelta
from pathlib import Path

from click.testing import CliRunner

from ord_plan.models.date_range import DateRange
from ord_plan.services.date_service import DateService


class TestDateProtection:
    """Test date protection and warning functionality."""

    def test_past_date_detection(self) -> None:
        """Test detection of past dates."""
        now = datetime.now()

        # Test date from previous week (before current week's Monday)
        # Go back enough days to ensure we're in the previous week
        days_to_previous_week = now.weekday() + 8  # Go to previous week's Monday
        past_date = now - timedelta(days=days_to_previous_week)
        date_range = DateRange(
            start_date=past_date.replace(hour=0, minute=0, second=0, microsecond=0),
            end_date=now,
        )

        assert date_range.has_past_dates()
        assert len(date_range.warnings) > 0
        # Should contain some mention of past dates (could be "past dates" or "more than 1 week in the past")
        warnings_text = " ".join(date_range.warnings).lower()
        assert any(
            phrase in warnings_text
            for phrase in [
                "past dates",
                "week in the past",
                "month in the past",
                "year in the past",
            ]
        )

    def test_week_ago_past_date_warning(self) -> None:
        """Test warning for dates more than 1 week ago."""
        now = datetime.now()

        # More than 1 week ago - go back at least 10 days from current week's Monday
        days_to_previous_week = (
            now.weekday() + 10
        )  # Go to previous week's Monday + 3 more days
        past_date = now - timedelta(days=days_to_previous_week)
        date_range = DateRange(
            start_date=past_date.replace(hour=0, minute=0, second=0, microsecond=0),
            end_date=now,
        )

        assert date_range.has_past_dates()
        assert any(
            "more than 1 week in the past" in warning for warning in date_range.warnings
        )

    def test_month_ago_past_date_warning(self) -> None:
        """Test warning for dates more than 1 month ago."""
        now = datetime.now()

        # More than 1 month ago
        past_date = now - timedelta(days=45)
        date_range = DateRange(
            start_date=past_date.replace(hour=0, minute=0, second=0, microsecond=0),
            end_date=now,
        )

        assert date_range.has_past_dates()
        assert any(
            "more than 1 month in the past" in warning
            for warning in date_range.warnings
        )

    def test_year_ago_past_date_warning(self) -> None:
        """Test warning for dates more than 1 year ago."""
        now = datetime.now()

        # More than 1 year ago
        past_date = now - timedelta(days=400)
        date_range = DateRange(
            start_date=past_date.replace(hour=0, minute=0, second=0, microsecond=0),
            end_date=now,
        )

        assert date_range.has_past_dates()
        assert any(
            "more than 1 year in the past" in warning for warning in date_range.warnings
        )

    def test_future_date_detection(self) -> None:
        """Test detection of distant future dates."""
        now = datetime.now()

        # More than 1 year in future
        future_date = now.replace(year=now.year + 2)
        date_range = DateRange(start_date=now, end_date=future_date)

        assert date_range.has_distant_future_dates()
        assert len(date_range.warnings) > 0
        assert any("future" in warning for warning in date_range.warnings)

    def test_one_year_future_no_warning(self) -> None:
        """Test that dates exactly 1 year in future don't trigger distant future warning."""
        now = datetime.now()

        # Exactly 1 year in future
        future_date = now.replace(year=now.year + 1)
        date_range = DateRange(start_date=now, end_date=future_date)

        assert not date_range.has_distant_future_dates()

    def test_two_years_future_warning(self) -> None:
        """Test warning for dates more than 2 years in future."""
        now = datetime.now()

        # More than 2 years in future
        future_date = now.replace(year=now.year + 3)
        date_range = DateRange(start_date=now, end_date=future_date)

        assert date_range.has_distant_future_dates()
        assert any(
            "more than 2 years in the future" in warning
            for warning in date_range.warnings
        )

    def test_date_protection_violations(self) -> None:
        """Test detection of date protection violations."""
        now = datetime.now()

        # Create date range with violations
        past_date = now - timedelta(days=45)  # More than 1 month past
        future_date = now.replace(year=now.year + 2)  # More than 1 year future

        date_range = DateRange(
            start_date=past_date.replace(hour=0, minute=0, second=0, microsecond=0),
            end_date=future_date,
        )

        violations = DateService.check_date_protection_violations(date_range)

        assert len(violations) >= 2
        assert any("more than 1 month" in v and "past" in v for v in violations)
        assert any("years in the future" in v for v in violations)

    def test_no_date_protection_violations(self) -> None:
        """Test that normal date ranges have no violations."""
        now = datetime.now()

        # Normal date range (current week)
        start_date = now - timedelta(days=now.weekday())
        end_date = start_date + timedelta(days=6)

        date_range = DateRange(
            start_date=start_date.replace(hour=0, minute=0, second=0, microsecond=0),
            end_date=end_date.replace(
                hour=23, minute=59, second=59, microsecond=999999
            ),
        )

        violations = DateService.check_date_protection_violations(date_range)

        assert len(violations) == 0
        assert not date_range.has_past_dates()
        assert not date_range.has_distant_future_dates()

    def test_date_range_summary_confirmation(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test date range summary for user confirmation."""
        from unittest.mock import patch

        # Create a test date range
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 1, 7)
        date_range = DateRange(start_date=start_date, end_date=end_date)

        # Test the confirmation function
        with patch("click.confirm", return_value=True) as mock_confirm:
            result = DateService.confirm_date_range(date_range)

            assert result is True
            mock_confirm.assert_called_once()

            # Check that confirm was called with some message (implementation may vary)
            call_args = mock_confirm.call_args
            assert len(call_args[0]) > 0  # Some message was passed to confirm

    def test_user_confirmation_prompt(self, runner: CliRunner) -> None:
        """Test enhanced user confirmation prompt."""
        from unittest.mock import patch

        with patch("click.confirm", return_value=False) as mock_confirm:
            result = DateService.prompt_user_confirmation("Test message", default=True)

            assert result is False
            mock_confirm.assert_called_once_with("Test message", default=True)

    def test_edge_case_dates(self) -> None:
        """Test edge cases for date protection."""
        now = datetime.now()

        # Test exactly at midnight today (should not be considered past)
        today_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        date_range = DateRange(start_date=today_midnight, end_date=now)

        # Should not trigger past date warnings if start is today
        past_warnings = [w for w in date_range.warnings if "past" in w.lower()]
        if date_range.start_date.date() == now.date():
            assert len(past_warnings) == 0

    def test_warning_accumulation(self) -> None:
        """Test that multiple warnings are accumulated correctly."""
        now = datetime.now()

        # Create date range with multiple issues
        start_date = now - timedelta(days=100)  # Past date
        end_date = now.replace(year=now.year + 3)  # Far future

        date_range = DateRange(
            start_date=start_date.replace(hour=0, minute=0, second=0, microsecond=0),
            end_date=end_date,
        )

        # Should have both past and future warnings
        warnings_text = " ".join(date_range.warnings).lower()
        assert "past" in warnings_text
        assert "future" in warnings_text

        # Should have multiple warnings
        assert len(date_range.warnings) >= 2
