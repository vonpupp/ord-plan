"""Unit tests for test-cron CLI command."""

from click.testing import CliRunner

from ord_plan.cli.test_cron import test_cron


def test_basic_cron_expression() -> None:
    """Test basic daily cron expression generates correct occurrences."""
    runner = CliRunner()
    result = runner.invoke(
        test_cron,
        ["--start", "2025-01-01", "--cron", "0 0 * * *", "--occurrences", "5"],
    )
    assert result.exit_code == 0
    assert "2025-01-01" in result.output
    assert "Upcoming occurrences:" in result.output
    assert "✓ Generated 5 occurrences" in result.output


def test_annual_cron_expression() -> None:
    """Test annual cron expression (December 1st) generates correct dates."""
    runner = CliRunner()
    result = runner.invoke(
        test_cron,
        ["--start", "2025-01-01", "--cron", "0 0 1 12 *", "--occurrences", "3"],
    )
    assert result.exit_code == 0
    assert "2025-12-01" in result.output
    assert "2026-12-01" in result.output
    assert "2027-12-01" in result.output
    assert "✓ Generated 3 occurrences" in result.output


def test_weekly_cron_expression() -> None:
    """Test weekly Monday cron expression generates correct dates."""
    runner = CliRunner()
    result = runner.invoke(
        test_cron,
        ["--start", "2025-01-01", "--cron", "0 9 * * 1", "--occurrences", "3"],
    )
    assert result.exit_code == 0
    assert "Upcoming occurrences:" in result.output
    assert "✓ Generated 3 occurrences" in result.output


def test_invalid_cron_expression() -> None:
    """Test invalid cron expression is properly rejected."""
    runner = CliRunner()
    result = runner.invoke(
        test_cron,
        ["--start", "2025-01-01", "--cron", "invalid cron", "--occurrences", "5"],
    )
    assert result.exit_code != 0
    assert "validation errors" in result.output


def test_invalid_date_format() -> None:
    """Test invalid date format is properly rejected."""
    runner = CliRunner()
    result = runner.invoke(
        test_cron,
        ["--start", "invalid-date", "--cron", "0 0 * * *", "--occurrences", "5"],
    )
    assert result.exit_code != 0
    assert "Invalid start date" in result.output


def test_negative_occurrences() -> None:
    """Test negative occurrences count is properly rejected."""
    runner = CliRunner()
    result = runner.invoke(
        test_cron,
        ["--start", "2025-01-01", "--cron", "0 0 * * *", "--occurrences", "-5"],
    )
    assert result.exit_code != 0
    assert "must be positive" in result.output


def test_zero_occurrences() -> None:
    """Test zero occurrences count is properly rejected."""
    runner = CliRunner()
    result = runner.invoke(
        test_cron,
        ["--start", "2025-01-01", "--cron", "0 0 * * *", "--occurrences", "0"],
    )
    assert result.exit_code != 0
    assert "must be positive" in result.output


def test_every_15_minutes() -> None:
    """Test complex pattern (every 15 minutes) generates correct occurrences."""
    runner = CliRunner()
    result = runner.invoke(
        test_cron,
        ["--start", "2025-01-01", "--cron", "*/15 * * * *", "--occurrences", "5"],
    )
    assert result.exit_code == 0
    assert "Upcoming occurrences:" in result.output
    assert "✓ Generated 5 occurrences" in result.output
