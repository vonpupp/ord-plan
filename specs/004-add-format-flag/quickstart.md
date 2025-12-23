# Quickstart Guide: Add Format Flag for Configuration Decoupling

**Feature**: 004-add-format-flag
**Date**: 2025-12-23
**Purpose**: Quick reference for using the new `--format` flag

## Overview

The `--format` flag allows you to separate formatting configuration from event rules, enabling:
- Reusable format configurations across multiple rules files
- Cleaner separation of concerns
- Easier maintenance of formatting options

## Before and After

### Before (Combined Format)

```bash
# Single file contains both formatting and events
ord-plan generate --rules my_events.yaml --from 2026-01-01 --to 2026-12-31
```

**File structure** (`my_events.yaml`):
```yaml
REVERSE_DATETREE_WEEK_FORMAT: "%Y-W%V"
REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d %a"
REVERSE_DATETREE_YEAR_FORMAT: "%Y"
REVERSE_DATETREE_USE_WEEK_TREE: true

events:
  - title: "Weekly Meeting"
    cron: "0 14 * * 2"
```

### After (Separated Format)

```bash
# Separate format file and events file
ord-plan generate \
  --format weekly_format.yaml \
  --rules my_events.yaml \
  --from 2026-01-01 \
  --to 2026-12-31
```

**File structure**:
- `weekly_format.yaml` (formatting only):
  ```yaml
  REVERSE_DATETREE_WEEK_FORMAT: "%Y-W%V"
  REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d %a"
  REVERSE_DATETREE_YEAR_FORMAT: "%Y"
  REVERSE_DATETREE_USE_WEEK_TREE: true
  ```

- `my_events.yaml` (events only):
  ```yaml
  events:
    - title: "Weekly Meeting"
      cron: "0 14 * * 2"
  ```

## Quick Examples

### Example 1: Weekly Format with Fiscal Events

**Format file** (`weekly_format.yaml`):
```yaml
REVERSE_DATETREE_WEEK_FORMAT: "%Y-W%V"
REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d %a"
REVERSE_DATETREE_YEAR_FORMAT: "%Y"
REVERSE_DATETREE_USE_WEEK_TREE: true
```

**Rules file** (`fiscal_events.yaml`):
```yaml
events:
  - title: "Tax report submission"
    cron: "0 0 1 8 *"
    tags: ["fiscal"]
  - title: "Income tax preparation"
    cron: "0 0 1 12 *"
    tags: ["fiscal"]
```

**Command**:
```bash
ord-plan generate \
  --format weekly_format.yaml \
  --rules fiscal_events.yaml \
  --from 2026-01-01 \
  --to 2026-12-20 \
  --file fiscal_2026.org
```

### Example 2: Monthly Format with Different Events

Reuse the same `weekly_format.yaml` with different events:

**Rules file** (`team_events.yaml`):
```yaml
events:
  - title: "Team Standup"
    cron: "0 9 * * 1,2,3,4,5"
    tags: ["team"]
  - title: "Sprint Review"
    cron: "0 15 * * 5"
    tags: ["team", "review"]
```

**Command**:
```bash
ord-plan generate \
  --format weekly_format.yaml \
  --rules team_events.yaml \
  --from 2026-01-01 \
  --to 2026-12-31 \
  --file team_2026.org
```

### Example 3: Override Rules File Format

**Format file** (`custom_format.yaml`):
```yaml
REVERSE_DATETREE_DATE_FORMAT: "%d/%m/%Y"
```

**Rules file** (`events.yaml`) - has its own formatting:
```yaml
REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d"
REVERSE_DATETREE_USE_WEEK_TREE: true

events:
  - title: "Meeting"
    cron: "0 10 * * 1"
```

**Command**:
```bash
ord-plan generate \
  --format custom_format.yaml \
  --rules events.yaml \
  --from 2026-01-01 \
  --to 2026-12-31
```

**Result**: Uses `"%d/%m/%Y"` from format file (precedence over rules file), uses `true` for week tree from rules file.

### Example 4: Backward Compatibility (No Format File)

**Rules file** (`events.yaml`) - combined format:
```yaml
REVERSE_DATETREE_WEEK_FORMAT: "%Y-W%V"
REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d %a"
REVERSE_DATETREE_YEAR_FORMAT: "%Y"
REVERSE_DATETREE_USE_WEEK_TREE: true

events:
  - title: "Meeting"
    cron: "0 10 * * 1"
```

**Command** (no format file):
```bash
ord-plan generate \
  --rules events.yaml \
  --from 2026-01-01 \
  --to 2026-12-31
```

**Result**: Same output as before `--format` flag was added.

## Format File Reference

### All Format Options

```yaml
REVERSE_DATETREE_WEEK_FORMAT: "%Y-W%V"    # Week format: 2026-W52
REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d %a" # Date format: 2026-12-25 Thu
REVERSE_DATETREE_YEAR_FORMAT: "%Y"          # Year format: 2026
REVERSE_DATETREE_USE_WEEK_TREE: true         # Enable week-based hierarchy
```

### Partial Format Files

You can specify only the options you want to override:

**Example** - Custom date format only:
```yaml
REVERSE_DATETREE_DATE_FORMAT: "%d/%m/%Y"
```

**Example** - Weekly tree only:
```yaml
REVERSE_DATETREE_USE_WEEK_TREE: true
```

### Empty Format File

Create an empty YAML file to use all defaults:
```yaml
# All formatting options will use defaults
```

## Common Patterns

### Reuse Format Across Projects

1. Create a `common_format.yaml`:
   ```yaml
   REVERSE_DATETREE_WEEK_FORMAT: "%Y-W%V"
   REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d %a"
   REVERSE_DATETREE_YEAR_FORMAT: "%Y"
   REVERSE_DATETREE_USE_WEEK_TREE: true
   ```

2. Use with different rules files:
   ```bash
   ord-plan generate --format common_format.yaml --rules project1_events.yaml --from 2026-01-01 --to 2026-12-31 --file project1.org
   ord-plan generate --format common_format.yaml --rules project2_events.yaml --from 2026-01-01 --to 2026-12-31 --file project2.org
   ```

### Migration from Combined to Separated

**Step 1**: Extract formatting from combined file
```bash
# Combined file: my_events.yaml
# Extract the REVERSE_DATETREE_* headers
```

**Step 2**: Create format file (`my_format.yaml`)
```yaml
REVERSE_DATETREE_WEEK_FORMAT: "%Y-W%V"
REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d %a"
REVERSE_DATETREE_YEAR_FORMAT: "%Y"
REVERSE_DATETREE_USE_WEEK_TREE: true
```

**Step 3**: Update rules file to events only (`my_events.yaml`)
```yaml
events:
  - title: "Meeting"
    cron: "0 10 * * 1"
```

**Step 4**: Update command
```bash
# Old command:
ord-plan generate --rules my_events.yaml --from 2026-01-01 --to 2026-12-31

# New command (same output):
ord-plan generate --format my_format.yaml --rules my_events.yaml --from 2026-01-01 --to 2026-12-31
```

## Troubleshooting

### Format File Not Found

```
Error: Format file /path/to/format.yaml does not exist
```

**Solution**: Check the file path is correct and file exists.

### Invalid Date Format

```
Configuration errors:
  - Date format "%Y-%m-%d" is invalid: invalid directive 'd'
```

**Solution**: Check date format string is valid for Python's `strftime()`.

### Unknown Configuration Key

```
YAML warnings:
  - Warning: Unknown configuration key 'CUSTOM_KEY' will be ignored
```

**Solution**: This is a warning, not an error. Check spelling or remove unused key.

### Format File Contains Events

```
Error: Format file must not contain 'events' section
```

**Solution**: Move `events` section to rules file, format file should only contain formatting options.

## Best Practices

1. **Use descriptive format file names**: `weekly_format.yaml`, `monthly_format.yaml`, `project_format.yaml`

2. **Version format files**: `format_v1.yaml`, `format_v2.yaml` when making changes

3. **Document format files**: Add comments explaining purpose:
   ```yaml
   # Weekly format for fiscal planning
   REVERSE_DATETREE_USE_WEEK_TREE: true
   REVERSE_DATETREE_WEEK_FORMAT: "%Y-W%V"
   ```

4. **Keep format files simple**: Only formatting options, no business logic

5. **Test with dry-run first**:
   ```bash
   ord-plan generate --format format.yaml --rules events.yaml --from 2026-01-01 --to 2026-12-31 --dry-run
   ```

## Additional Resources

- **Feature specification**: [spec.md](./spec.md)
- **CLI contract**: [contracts/cli.md](./contracts/cli.md)
- **Data model**: [data-model.md](./data-model.md)
- **Implementation plan**: [plan.md](./plan.md)
- **Research findings**: [research.md](./research.md)
