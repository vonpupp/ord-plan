"""Generate command for ord-plan."""

from typing import Optional

import click

from ..cli.config import Configuration
from ..parsers.org_mode import OrgModeParser
from ..parsers.yaml_parser import YamlParser
from ..services.date_service import DateService
from ..services.event_service import EventService
from ..services.file_service import FileService
from ..utils.validators import validate_cron_expression
from ..utils.validators import validate_date_format
from ..utils.validators import validate_file_path
from ..utils.validators import validate_file_readable
from ..utils.validators import validate_file_writable


@click.command(
    epilog="""
  # Basic usage with default date range (current week)
  ord-plan generate --rules my-events.yaml --file tasks.org

   # Custom date range for specific month
   ord-plan generate --rules events.yaml --from 2025-01-01 --to 2025-01-31 \
         --file january.org

  # Generate for next 30 days with relative dates
  ord-plan generate --rules events.yaml --from today --to "+30 days"

  # Override date warnings (use with caution)
  ord-plan generate --rules events.yaml --from 2024-01-01 --to 2024-12-31 --force

  # Output to terminal to preview before saving
  ord-plan generate --rules events.yaml --from today --to "+7 days"

Date Formats:
  - Absolute: YYYY-MM-DD (e.g., 2025-01-15)
  - Relative: today, tomorrow, yesterday, next monday, next week, next month, next year
  - Offset: +N days (e.g., +7 days for one week from now)

 For detailed help with examples, visit: https://github.com/vonpupp/ord-plan
"""
)
@click.option(
    "--rules",
    required=True,
    type=click.Path(exists=True, readable=True),
    help="""Path to YAML rules file containing event definitions.

    Example rules file format:
    events:
      - title: "Morning Exercise"
        cron: "0 7 * * 1,3,5"
        tags: ["health", "exercise"]
      - title: "Team Meeting"
        cron: "0 14 * * 2"
        todo_state: "TODO"
        description: "Weekly team sync""",
)
@click.option(
    "--format",
    type=click.Path(exists=True, readable=True),
    help="""Path to YAML format configuration file.

    Contains only formatting options (REVERSE_DATETREE_WEEK_FORMAT, etc.).
    Format file options take precedence over rules file options.""",
)
@click.option(
    "--file",
    type=click.Path(),
    help="""Path to target org-mode file.
    If not specified, output goes to stdout.
    Existing files are preserved, new events are appended.
    Non-existent files are created.""",
)
@click.option(
    "--from",
    "from_date",
    type=str,
    help="""Start date for event generation.

     Formats: YYYY-MM-DD, today, tomorrow, yesterday, next [day], next \
week/month/year, +N days
     Default: Monday of current week""",
)
@click.option(
    "--to",
    "to_date",
    type=str,
    help="""End date for event generation.

     Formats: YYYY-MM-DD, today, tomorrow, yesterday, next [day], next \
week/month/year, +N days
     Default: Sunday of current week""",
)
@click.option(
    "--force",
    is_flag=True,
    help="""Bypass past/future date warnings.

    Use with caution when generating events for:
    - Dates more than 1 month in the past
    - Dates more than 1 year in the future

    This flag automatically confirms all warning prompts.""",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="""Show what would be generated without creating/modifying files.

    Useful for testing and previewing output before committing changes.""",
)
def generate(
    rules: str,
    format: Optional[str],
    file: Optional[str],
    from_date: Optional[str],
    to_date: Optional[str],
    force: bool,
    dry_run: bool,
) -> None:
    """Generate org-mode events from cron-based rules.

    This command reads a YAML file containing event definitions with cron expressions
    and generates a hierarchical org-mode file with scheduled events.

    The output preserves existing content and adds new events in a structured
    date hierarchy: Year > Week > Date > Events.
    """

    # Enhanced file path validation
    path_errors = validate_file_path(rules)
    if path_errors:
        click.echo("Error: " + "; ".join(path_errors), err=True)
        raise click.Abort()

    # Validate rules file readability
    file_errors = validate_file_readable(rules)
    if file_errors:
        click.echo("Error: " + "; ".join(file_errors), err=True)
        raise click.Abort()

    # Validate target file if specified
    if file:
        # Enhanced file path validation for target file
        target_path_errors = validate_file_path(file)
        if target_path_errors:
            click.echo("Error: " + "; ".join(target_path_errors), err=True)
            raise click.Abort()

        # Validate file writability
        file_errors = validate_file_writable(file)
        if file_errors:
            click.echo("Error: " + "; ".join(file_errors), err=True)
            raise click.Abort()

    # Validate format file if provided
    format_config = None
    format_errors = []
    if format:
        # Enhanced file path validation for format file
        format_path_errors = validate_file_path(format)
        if format_path_errors:
            click.echo("Error: " + "; ".join(format_path_errors), err=True)
            raise click.Abort()

        # Validate format file readability
        format_read_errors = validate_file_readable(format)
        if format_read_errors:
            click.echo("Error: " + "; ".join(format_read_errors), err=True)
            raise click.Abort()

        # Parse format file
        try:
            format_config = YamlParser.parse_format_file(format)
            format_errors = YamlParser.validate_format_schema(format_config)

            # Separate errors from warnings
            errors = [err for err in format_errors if not err.startswith("Warning:")]
            warnings = [warn for warn in format_errors if warn.startswith("Warning:")]

            if errors:
                click.echo("Format file validation errors:", err=True)
                for error in errors:
                    click.echo(f"  - {error}", err=True)
                raise click.Abort()

            if warnings:
                click.echo("Format file warnings:", err=True)
                for warning in warnings:
                    click.echo(f"  - {warning}", err=True)
        except Exception as e:
            click.echo(f"Format file error: {e}", err=True)
            raise click.Abort() from e

    # Validate date formats if provided
    if from_date:
        date_errors = validate_date_format(from_date, "--from date")
        if date_errors:
            click.echo("Error: " + "; ".join(date_errors), err=True)
            raise click.Abort()

    if to_date:
        date_errors = validate_date_format(to_date, "--to date")
        if date_errors:
            click.echo("Error: " + "; ".join(date_errors), err=True)
            raise click.Abort()

    # Enhanced YAML parsing with schema validation
    try:
        config, schema_errors = YamlParser.parse_and_validate(rules)
        if schema_errors:
            # Separate errors from warnings
            errors = [err for err in schema_errors if not err.startswith("Warning:")]
            warnings = [warn for warn in schema_errors if warn.startswith("Warning:")]

            if errors:
                click.echo("YAML validation errors:", err=True)
                for error in errors:
                    click.echo(f"  - {error}", err=True)
                raise click.Abort()

            if warnings:
                click.echo("YAML warnings:", err=True)
                for warning in warnings:
                    click.echo(f"  - {warning}", err=True)
    except Exception as e:
        click.echo(f"YAML parsing error: {e}", err=True)
        raise click.Abort() from e

    # Parse event rules
    try:
        event_rules = YamlParser.parse_event_rules(config)
    except ValueError as err:
        click.echo(f"Error parsing event rules: {err}", err=True)
        raise click.Abort() from err

    # Validate cron expressions for all rules
    cron_errors = []
    for rule in event_rules:
        errors = validate_cron_expression(rule.cron, rule.title)
        cron_errors.extend(errors)

    if cron_errors:
        click.echo("Cron expression validation errors:", err=True)
        for error in cron_errors:
            click.echo(f"  - {error}", err=True)
        raise click.Abort()

    # Parse enhanced configuration with format file merge
    try:
        app_config = Configuration.merge_format_config(config, format_config)

        # Validate configuration
        config_errors = app_config.validate_date_formats()
        if config_errors:
            click.echo("Configuration errors:", err=True)
            for error in config_errors:
                click.echo(f"  - {error}", err=True)
            raise click.Abort()

    except Exception as e:
        click.echo(f"Error processing file {file}: {e}", err=True)
        raise click.Abort() from e

    # Parse date range
    date_range = DateService.parse_date_range(from_date, to_date)

    # Validate date range with protection checks
    if not DateService.validate_date_range(date_range, force):
        click.echo("Aborted.", err=True)
        raise click.Abort()
    elif force and date_range.warnings:
        # Show warnings even when forcing so user knows what was bypassed
        click.echo("ℹ️  Note: Bypassing following warnings with --force:", err=True)
        for warning in date_range.warnings:
            click.echo(f"  - {warning}", err=True)

    # Handle dry-run mode
    if dry_run:
        click.echo("🔍 DRY RUN MODE - No files will be modified", err=True)
        click.echo(f"   Rules file: {rules}")
        click.echo(
            f"   Date range: {date_range.start_date.strftime('%Y-%m-%d')} to "
            f"{date_range.end_date.strftime('%Y-%m-%d')}"
        )
        click.echo(f"   Events to generate: ~{len(event_rules) * 7} (estimated)")
        click.echo("   Use --force to proceed with actual file generation", err=True)
        return

    # Read existing content if file exists
    existing_nodes = []
    if file:
        existing_nodes = OrgModeParser.read_existing_content(file)

    # Generate events
    date_nodes = EventService.generate_complete_event_set(
        event_rules, date_range, existing_nodes, app_config.default_todo_state
    )

    # Render content
    content = OrgModeParser.render_org_content(date_nodes)

    # Output content using FileService
    if file:
        try:
            # Get file stats before processing
            stats_before = FileService.get_file_content_stats(file)
            if stats_before["exists"]:
                click.echo(f"Reading existing file: {file}")
                click.echo(f"  Existing events: {stats_before['events']}")

            # Write content using FileService
            FileService.write_org_content(content, file)

            # Show summary
            total_events = sum(
                len(node.existing_events) + len(node.new_events) for node in date_nodes
            )
            new_events = sum(len(node.new_events) for node in date_nodes)

            click.echo(f"Events written to {file}")
            click.echo(f"  Total events: {total_events}")
            click.echo(f"  New events added: {new_events}")
            if stats_before["exists"]:
                click.echo(f"  Existing events preserved: {stats_before['events']}")

        except Exception as e:
            click.echo(f"Unexpected error: {e}", err=True)
            click.echo(
                "This appears to be an internal error. Please report this issue.",
                err=True,
            )
            raise click.Abort() from e
    else:
        click.echo(content)
