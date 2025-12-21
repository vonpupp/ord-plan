# Quickstart Guide: Generate Org Events from Cron Rules

**Purpose**: Get started with the `ord-plan generate` command quickly

## Installation

Ensure you have the required dependencies installed:

```bash
pip install croniter orgparse pyyaml click
```

## Basic Usage

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
```

### 2. Generate Events for Next Week

```bash
ord-plan generate --rules my-rules.yaml --file tasks.org
```

This creates a hierarchical org-mode file like:

```org
* 2025
** 2025-W51
*** 2025-12-16 Mon
**** TODO Morning Exercise                       :health:exercise:
**** TODO Team Meeting                             :work:meeting:
*** 2025-12-18 Wed
**** TODO Morning Exercise                       :health:exercise:
```

### 3. Add to Existing Org File

If `tasks.org` already exists, new events are added without modifying existing content:

```bash
ord-plan generate --rules my-rules.yaml --file existing-tasks.org
```

## Advanced Usage

### Custom Date Ranges

Generate events for specific periods:

```bash
# January 2025
ord-plan generate --rules my-rules.yaml --from 2025-01-01 --to 2025-01-31 --file january.org

# Next 30 days
ord-plan generate --rules my-rules.yaml --from today --to "+30 days" --file upcoming.org
```

### Output to Terminal

Check what will be generated before writing to file:

```bash
ord-plan generate --rules my-rules.yaml --from today --to "+7 days"
```

### Force Past Date Generation

Override warnings about generating past events:

```bash
ord-plan generate --rules my-rules.yaml --from 2024-12-01 --to 2024-12-31 --file review.org --force
```

## Cron Expression Examples

| Schedule                | Cron Expression | Description               |
| ----------------------- | --------------- | ------------------------- |
| Daily at 9 AM           | `0 9 * * *`     | Every day at 9:00         |
| Weekdays at 2 PM        | `0 14 * * 1-5`  | Monday-Friday at 14:00    |
| Monday/Wednesday/Friday | `0 0 * * 1,3,5` | Mon, Wed, Fri at midnight |
| First of month          | `0 0 1 * *`     | 1st day of each month     |
| Every 2 hours           | `0 */2 * * *`   | Every 2 hours on the hour |

## Event Configuration Options

### Complex Event Example

```yaml
events:
  - title: "Development Sprint"
    cron: "0 9 * * 1,2,3,4,5"
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

## Common Workflows

### Workflow 1: Personal Task Management

1. Create rules for recurring personal activities
2. Generate weekly tasks every Sunday
3. Add manual tasks to generated file
4. Track completion in org-mode

### Workflow 2: Team Planning

1. Define team meeting and deadline schedules
2. Generate monthly or quarterly planning files
3. Share with team for coordination
4. Update individual task lists

### Workflow 3: Project Templates

1. Create project-specific rule sets
2. Generate baseline project schedules
3. Customize for specific projects
4. Maintain template library

## Troubleshooting

### Common Issues

**"Invalid cron expression"**

- Check cron syntax format: `minute hour day month weekday`
- Use numbers (0-6) for weekdays, not names

**"File not found"**

- Verify file paths are correct
- Use absolute paths if needed
- Check file permissions

**"No events generated"**

- Verify cron expressions match your date range
- Check that weekdays in cron align with your target dates
- Try a broader date range for testing

### Getting Help

```bash
ord-plan generate --help
```

View detailed help for all command options and examples.
