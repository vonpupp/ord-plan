# CLI Contract: Add Format Flag for Configuration Decoupling

**Feature**: 004-add-format-flag
**Date**: 2025-12-23
**Purpose**: Define CLI interface contract for `--format` flag

## Command

### `ord-plan generate`

Generate org-mode events from cron-based rules.

#### Signature

```bash
ord-plan generate \
  --rules <rules-file> \
  [--format <format-file>] \
  [--file <output-file>] \
  [--from <start-date>] \
  [--to <end-date>] \
  [--force] \
  [--dry-run]
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--rules` | file path | Yes | Path to YAML rules file containing event definitions |
| `--format` | file path | No | Path to YAML format configuration file |
| `--file` | file path | No | Path to target org-mode file |
| `--from` | date string | No | Start date for event generation |
| `--to` | date string | No | End date for event generation |
| `--force` | flag | No | Bypass past/future date warnings |
| `--dry-run` | flag | No | Show what would be generated without creating files |

#### Return Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (invalid input, validation failure, file I/O error) |
| 2 | User aborted |

## New Parameter: `--format`

### Description

Path to YAML format configuration file containing only formatting options for org-mode output.

### Type

`click.Path(exists=True, readable=True)`

### Required

No (optional parameter)

### Default Value

None (use rules file formatting or defaults)

### Behavior

#### When Not Provided

- Use formatting options from rules file if present
- If rules file has no formatting options, use Configuration defaults

#### When Provided

- Parse format file YAML
- Validate format file structure
- Merge format file options with rules file options
- Format file options take precedence over rules file options
- Use Configuration defaults for missing options

### Validation

#### File-Level Validation

| Check | Behavior on Failure |
|--------|----------------------|
| File exists | Error: "Error: Format file {path} does not exist" |
| File readable | Error: "Error: Format file {path} is not readable" |
| Valid YAML | Error: "YAML parsing error: {details}" |

#### Content-Level Validation

| Check | Behavior on Failure |
|--------|----------------------|
| No `events` section allowed | Error: "Error: Format file must not contain 'events' section" |
| Valid date format strings | Error: "Configuration errors: {format} is invalid: {details}" |
| Unknown configuration keys | Warning to stderr: "Warning: Unknown configuration key {key} will be ignored" |

### Allowed Format Keys

| Key | Type | Default | Description |
|-----|------|----------|-------------|
| REVERSE_DATETREE_YEAR_FORMAT | string | "%Y" | Format string for year-level headlines |
| REVERSE_DATETREE_WEEK_FORMAT | string | "%Y-W%V" | Format string for week-level headlines |
| REVERSE_DATETREE_DATE_FORMAT | string | "%Y-%m-%d %a" | Format string for date-level headlines |
| REVERSE_DATETREE_USE_WEEK_TREE | boolean | true | Whether to use week-based hierarchy |

### Example Format Files

#### Valid Format File

```yaml
REVERSE_DATETREE_WEEK_FORMAT: "%Y-W%V"
REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d %a"
REVERSE_DATETREE_YEAR_FORMAT: "%Y"
REVERSE_DATETREE_USE_WEEK_TREE: true
```

#### Empty Format File (Uses All Defaults)

```yaml
# All formatting options will use defaults
```

#### Partial Format File

```yaml
REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d"
# Other options use defaults
```

## Usage Examples

### Example 1: Separate Format and Events Files

```bash
ord-plan generate \
  --format tests/fixtures/test_format_weekly_example.yaml \
  --rules tests/fixtures/test_fiscal_body.yaml \
  --from 2026-01-01 \
  --to 2026-12-20 \
  --file output.org
```

**Behavior**:
- Reads formatting options from `test_format_weekly_example.yaml`
- Reads events from `test_fiscal_body.yaml`
- Merges formatting and events
- Generates org-mode output to `output.org`

### Example 2: Backward Compatibility (No Format File)

```bash
ord-plan generate \
  --rules tests/fixtures/test_fiscal_body.yaml \
  --from 2026-01-01 \
  --to 2026-12-20
```

**Behavior**:
- Reads combined rules file with both formatting and events
- Uses formatting options from rules file
- Same behavior as before `--format` flag was added

### Example 3: Format File Overrides Rules File

```bash
ord-plan generate \
  --format weekly_format.yaml \
  --rules monthly_events.yaml \
  --from 2026-01-01 \
  --to 2026-12-31
```

**Behavior**:
- If `monthly_events.yaml` has `REVERSE_DATETREE_DATE_FORMAT: "%d/%m/%Y"`
- And `weekly_format.yaml` has `REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d"`
- Output uses `"%Y-%m-%d"` from format file (precedence)

### Example 4: Dry Run Preview

```bash
ord-plan generate \
  --format weekly_format.yaml \
  --rules monthly_events.yaml \
  --from 2026-01-01 \
  --to 2026-12-31 \
  --dry-run
```

**Behavior**:
- Shows preview without creating files
- Displays format file path and rules file path
- Displays date range and estimated event count

## Error Messages

### Format File Errors

```
Error: Format file /path/to/format.yaml does not exist
```

```
Error: Format file /path/to/format.yaml is not readable
```

```
YAML parsing error: Invalid YAML in /path/to/format.yaml: mapping values are not allowed here
```

```
Error: Format file must not contain 'events' section
```

```
Configuration errors:
  - Week format "%Y-%m-%d" is invalid: 'm' is a bad directive in format '%Y-%m-%d'
```

### Warnings

```
YAML warnings:
  - Warning: Unknown configuration key 'CUSTOM_OPTION' will be ignored
```

## Help Text

```
Usage: ord-plan generate [OPTIONS]

  Generate org-mode events from cron-based rules.

Options:
  --rules TEXT                 Path to YAML rules file containing event
                              definitions.  [required]
  --format PATH                Path to YAML format configuration file.
                              Contains only formatting options
                              (REVERSE_DATETREE_WEEK_FORMAT, etc.).
                              Format file options take precedence over
                              rules file options.
  --file PATH                  Path to target org-mode file. If not
                              specified, output goes to stdout.
  --from, --to TEXT            Start/End date for event generation.
  --force                      Bypass past/future date warnings.
  --dry-run                    Show what would be generated without
                              creating/modifying files.
  --help                       Show this message and exit.
```

## Backward Compatibility Guarantees

### Existing Commands

All existing commands work unchanged:

```bash
# Works exactly as before
ord-plan generate --rules events.yaml --from 2026-01-01 --to 2026-12-31
```

### Existing Rules Files

All existing rules files continue to work:

- Combined files with formatting + events → Use formatting from rules file
- Files with only events → Use Configuration defaults (if no format file provided)

### Default Behavior

When `--format` is not provided:
- Use formatting options from rules file (if present)
- Use Configuration defaults (if rules file has no formatting)
- Same output as before `--format` flag was added

## Precedence Rules

When multiple sources provide formatting options, precedence is:

1. Environment variables (e.g., `ORD_PLAN_YEAR_FORMAT`)
2. Format file options (if `--format` provided)
3. Rules file options (if present in rules file)
4. Configuration defaults

## Integration Points

### Input Validation

1. Validate `--rules` file path (existing)
2. Validate `--format` file path (new)
3. Parse and validate both YAML files
4. Validate all date format strings
5. Validate all cron expressions

### Configuration Merging

1. Load default Configuration
2. Apply rules file formatting options
3. Apply format file formatting options (overwrites rules)
4. Apply environment variable overrides
5. Validate merged configuration

### Error Reporting

1. Parse all input files
2. Collect all validation errors
3. Report all errors together
4. Abort if any errors found
5. Show warnings for non-critical issues
