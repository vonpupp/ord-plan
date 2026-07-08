"""Test cron expressions command for ord-plan."""

from datetime import datetime, timedelta

import click

from ..utils.validators import validate_cron_expression


@click.command(
    epilog="""
  # Test basic daily cron expression
  ord-plan test-cron --start 2025-01-01 --cron "0 0 * * *" --occurrences 5

  # Test annual event (December 1st)
  ord-plan test-cron --start 2025-01-01 --cron "0 0 1 12 *" --occurrences 5

  # Test weekly recurring events (Mondays at 9am)
  ord-plan test-cron --start 2025-01-01 --cron "0 9 * * 1" --occurrences 10

  # Test complex patterns (every 15 minutes)
  ord-plan test-cron --start 2025-01-01 --cron "*/15 * * * *" --occurrences 20

  For detailed help with examples, visit: https://github.com/vonpupp/ord-plan
"""
)
@click.option(
    "--start",
    "start_date",
    required=True,
    type=str,
    help="""Start date in YYYY-MM-DD format.

    Example: 2025-01-01 for January 1, 2025""",
)
@click.option(
    "--cron",
    "cron_expression",
    required=True,
    type=str,
    help="""Cron expression to test.

    Format: minute hour day month weekday
    Example: '0 0 1 12 *' for December 1st at midnight""",
)
@click.option(
    "--occurrences",
    "n_occurrences",
    required=True,
    type=int,
    help="""Number of occurrences to generate.

    Must be a positive integer""",
)
def test_cron(start_date: str, cron_expression: str, n_occurrences: int) -> None:
    """Test cron expressions and show upcoming occurrences.

    This command validates a cron expression and displays the next n occurrences
    starting from a specified date. Useful for verifying cron expressions before
    using them in event rules.
    """
    # Validate occurrences count
    if n_occurrences <= 0:
        click.echo(
            f"Error: occurrences must be positive, got {n_occurrences}", err=True
        )
        raise click.Abort()

    # Validate cron expression
    errors = validate_cron_expression(cron_expression, "test-cron")
    if errors:
        click.echo("Cron expression validation errors:", err=True)
        for error in errors:
            click.echo(f"  - {error}", err=True)
        raise click.Abort()

    # Parse start date using DateService (supports YYYY-MM-DD and relative dates)
    from ..services.date_service import DateService

    try:
        start_dt = DateService._parse_single_date(start_date)
    except (ValueError, click.BadParameter) as err:
        click.echo(f"Error: Invalid start date: {start_date}", err=True)
        click.echo("Expected format: YYYY-MM-DD (e.g., 2025-01-01)", err=True)
        raise click.Abort() from err

    # Generate occurrences using croniter
    from croniter import croniter

    cron = croniter(cron_expression, start_dt - timedelta(microseconds=1))

    click.echo(f"Cron expression: {cron_expression}")
    click.echo(f"Start date: {start_dt.strftime('%Y-%m-%d')}")
    click.echo(f"Number of occurrences: {n_occurrences}")
    click.echo()
    click.echo("Upcoming occurrences:")

    for i in range(n_occurrences):
        occurrence = cron.get_next(datetime)
        date_str = occurrence.strftime("%Y-%m-%d %H:%M:%S")
        day_name = occurrence.strftime("%A")
        click.echo(f"  {i + 1}. {date_str} ({day_name})")

    click.echo(f"\n✓ Generated {n_occurrences} occurrences")
