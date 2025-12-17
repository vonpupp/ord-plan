# Usage

## Overview

`ord-plan` is a CLI tool for generating org-mode events from cron-based YAML rules. It helps you create structured task schedules automatically while preserving existing content in your org files.

## Quick Start

### 1. Create a Rules File

Create `my-rules.yaml` with your recurring events:

```yaml
REVERSE_DATETREE_WEEK_FORMAT: "%Y-W%V"
REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d %a"
REVERSE_DATETREE_YEAR_FORMAT: "%Y"

events:
  - title: "Morning Exercise"
    cron: "0 7 * * 1,3,5"
    tags: ["health", "exercise"]
  - title: "Team Meeting"
    cron: "0 14 * * 2"
    todo_state: "TODO"
    tags: ["work", "meeting"]
    description: |
      - [ ] Review agenda
      - [ ] Prepare updates
      - [ ] Assign action items
```

### 2. Generate Events

```bash
# Generate for this week (default behavior)
ord-plan generate --rules my-rules.yaml --file tasks.org

# Generate for specific date range
ord-plan generate --rules my-rules.yaml --from 2025-01-01 --to 2025-01-31 --file january.org

# Preview output before saving
ord-plan generate --rules my-rules.yaml --from today --to "+7 days"
```

## Command Reference

### `ord-plan generate`

Generate org-mode events from cron-based rules.

#### Options

| Option | Required | Description |
|---------|-----------|-------------|
| `--rules PATH` | Yes | Path to YAML rules file containing event definitions |
| `--file PATH` | No | Path to target org-mode file (default: stdout) |
| `--from DATE` | No | Start date for event generation (default: Monday of current week) |
| `--to DATE` | No | End date for event generation (default: Sunday of current week) |
| `--force` | No | Bypass past/future date warnings (use with caution) |
| `--dry-run` | No | Show what would be generated without creating files |

#### Date Formats

- **Absolute**: `YYYY-MM-DD` (e.g., `2025-01-15`)
- **Relative**: `today`, `tomorrow`, `yesterday`, `next monday`, `next week`, `next month`, `next year`
- **Offset**: `+N days` (e.g., `+7 days` for one week from now)

## Usage Examples

### Basic Examples

#### Generate Events for Current Week

```bash
ord-plan generate --rules my-events.yaml --file weekly-tasks.org
```

Output structure:
```org
* 2025
** 2025-W03
*** 2025-01-20 Mon
**** TODO Morning Exercise                     :health:exercise:
**** TODO Team Meeting                        :work:meeting:
*** 2025-01-22 Wed
**** TODO Morning Exercise                     :health:exercise:
```

#### Custom Date Range

```bash
# Generate for January 2025
ord-plan generate --rules events.yaml --from 2025-01-01 --to 2025-01-31 --file january.org

# Generate for next 30 days
ord-plan generate --rules events.yaml --from today --to "+30 days" --file upcoming.org

# Generate for next month
ord-plan generate --rules events.yaml --from next month --to "+30 days" --file february.org
```

#### Working with Existing Files

```bash
# Add events to existing org file (preserves current content)
ord-plan generate --rules work-events.yaml --file existing-work.org

# Check what would be added without modifying file
ord-plan generate --rules work-events.yaml --file existing-work.org --dry-run
```

### Advanced Examples

#### Override Date Warnings

```bash
# Generate events for past dates (with confirmation or --force)
ord-plan generate --rules review.yaml --from 2024-12-01 --to 2024-12-31 --force

# Generate events far in future (with confirmation or --force)
ord-plan generate --rules planning.yaml --from 2026-01-01 --to 2026-12-31 --force
```

#### Complex Event Rules

```yaml
events:
  - title: "Development Sprint"
    cron: "0 9 * * 1-5"
    todo_state: "INPROGRESS"
    tags: ["work", "development", "focus"]
    description: |
      Deep work session for development tasks.
      - [ ] Review today's goals
      - [ ] Work on priority tickets
      - [ ] Update progress tracking
      
  - title: "Weekly Review"
    cron: "0 16 * * 5"
    todo_state: "TODO"
    tags: ["work", "planning", "review"]
    description: |
      End of week review and planning session.
      Important for maintaining project momentum.
```

## Configuration

### Environment Variables

Override configuration using environment variables:

```bash
export ORD_PLAN_YEAR_FORMAT="%Y"
export ORD_PLAN_WEEK_FORMAT="%Y Week %W"  
export ORD_PLAN_DATE_FORMAT="%B %d, %Y"
export ORD_PLAN_DEFAULT_TODO_STATE="TODO"
export ORD_PLAN_MAX_EVENTS="5000"
export ORD_PLAN_TIMEOUT="60"
```

### YAML Configuration File

Customize formatting in your rules file:

```yaml
# Custom date formats
REVERSE_DATETREE_YEAR_FORMAT: "%Y"
REVERSE_DATETREE_WEEK_FORMAT: "Week %W, %Y"
REVERSE_DATETREE_DATE_FORMAT: "%A, %B %d, %Y"

# Performance limits
max_events_per_file: 5000
processing_timeout_seconds: 60

events:
  - title: "Custom Formatted Event"
    cron: "0 9 * * 1"
```

## Cron Expression Examples

Common cron patterns for event scheduling:

| Schedule | Cron Expression | Description |
|-----------|----------------|-------------|
| Daily at 9 AM | `0 9 * * *` | Every day at 9:00 AM |
| Weekdays at 2 PM | `0 14 * * 1-5` | Monday-Friday at 2:00 PM |
| Monday/Wednesday/Friday | `0 0 * * 1,3,5` | Mon, Wed, Fri at midnight |
| First of month | `0 0 1 * *` | 1st day of each month |
| Every 2 hours | `0 */2 * * *` | Every 2 hours on the hour |
| Work days 9-5 | `0 9-17 * * 1-5` | Hourly from 9 AM to 5 PM, weekdays |

## Performance Considerations

### Large Date Ranges

For date ranges generating more than 1000 events, consider:
- Using smaller date ranges (e.g., monthly instead of yearly)
- Using more specific cron expressions to reduce matches
- Setting `ORD_PLAN_MAX_EVENTS` environment variable

### File Size Guidelines

- **Small files** (<100 events): Excellent performance
- **Medium files** (100-1000 events): Good performance
- **Large files** (>1000 events): May take longer, consider chunking

## Troubleshooting

### Common Issues

**"Invalid cron expression"**
- Check format: `minute hour day month weekday` (5 fields)
- Use numbers for weekdays: 0=Sunday, 6=Saturday
- Example: `0 9 * * 1-5` (9 AM on weekdays)

**"File cannot be read"**
- Check file path and permissions
- Use absolute paths if needed
- Verify file exists with `ls -la path/to/file.yaml`

**"No events generated"**
- Verify cron expressions match your date range
- Check that weekdays in cron align with target dates
- Try a broader date range for testing

### Debug Mode

Use `--dry-run` to preview output without modifying files:

```bash
ord-plan generate --rules debug.yaml --from 2025-01-01 --to 2025-01-07 --dry-run
```

### Getting Help

```bash
# Full command help
ord-plan generate --help

# Show version
ord-plan --version
```

## Integration Examples

### With Task Managers

```bash
# Generate monthly and import into your task manager
ord-plan generate --rules gtd.yaml --from 2025-01-01 --to 2025-01-31 --file monthly-gtd.org
```

### With Project Management

```bash
# Generate project schedules
ord-plan generate --rules project.yaml --from next monday --to "+14 days" --file sprint-1.org
```

### With Personal Organization

```bash
# Generate personal routines
ord-plan generate --rules personal.yaml --from today --to "+7 days" --file this-week.org
```

## Advanced Features

### Backup Protection

When working with important files:

```bash
# Enable backup via environment
export ORD_PLAN_BACKUP_FILES="true"
ord-plan generate --rules important.yaml --file critical.org
```

### Custom Date Hierarchies

```yaml
# Weekly hierarchy with custom formatting
REVERSE_DATETREE_YEAR_FORMAT: "Year %Y"
REVERSE_DATETREE_WEEK_FORMAT: "Week %W"  
REVERSE_DATETREE_DATE_FORMAT: "%A - %B %d"

events:
  - title: "Weekly Planning"
    cron: "0 9 * * 1"
```

Output:
```org
* Year 2025
** Week 03
*** Monday - January 20
**** TODO Weekly Planning
```
