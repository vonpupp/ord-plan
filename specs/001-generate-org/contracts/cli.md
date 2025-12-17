# CLI Contract: ord-plan generate

**Command**: `ord-plan generate`
**Purpose**: Generate org-mode events from cron-based rules

## Command Signature

```bash
ord-plan generate --rules <path> [--file <path>] [--from <date>] [--to <date>] [--force]
```

## Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|------------|------|-------------|------------|
| `--rules` | string | Path to YAML rules file | File must exist, valid YAML format |

### Optional Parameters

| Parameter | Type | Description | Default | Validation |
|------------|------|-------------|----------|------------|
| `--file` | string | Path to target org-mode file | stdout | File path must be writable |
| `--from` | string | Start date for event generation | Next Monday | Valid date format (YYYY-MM-DD) |
| `--to` | string | End date for event generation | Next Sunday | Valid date format (YYYY-MM-DD) |
| `--force` | flag | Bypass past/future date warnings | False | N/A |

## Date Format Handling

- **Input dates**: Accept YYYY-MM-DD format
- **Default behavior**: When no dates specified, generate for current Monday to Sunday
- **Date validation**: From date must be <= To date
- **Relative dates**: Support "today", "tomorrow", "next monday" for --from parameter

## Output Formats

### Standard Output (Default)
- All content written to specified file or stdout
- Hierarchical org-mode structure with proper nesting
- Preserves existing content when writing to files

### Error Output (stderr)
- Validation errors with file context and line numbers
- Warning messages for past/future dates without --force
- Progress information for large operations

## Exit Codes

| Code | Meaning | Description |
|-------|----------|-------------|
| 0 | Success | Events generated successfully |
| 1 | Invalid Input | Bad arguments, missing files, or validation errors |
| 2 | Permission Error | Cannot read rules file or write target file |
| 3 | Cron Expression Error | Invalid cron syntax in rules file |
| 4 | YAML Parsing Error | Invalid YAML structure in rules file |

## Input Validation Rules

### Rules File Validation
- File must exist and be readable
- Must contain valid YAML structure
- Required fields: `events` array with valid event objects
- Each event must have `title` and `cron` fields
- Cron expressions must be valid croniter format

### Date Range Validation
- Dates must be in YYYY-MM-DD format or parseable relative dates
- From date must be <= To date
- Past dates trigger warning unless --force used
- Future dates beyond 1 year trigger warning unless --force used

### Target File Validation
- If file exists, must be writable
- If file doesn't exist, directory must be writable
- Existing content must be valid org-mode (best effort)

## Performance Specifications
- Concurrent access: No special handling (filesystem permissions only)

## Examples

```bash
# Basic usage with default date range
ord-plan generate --rules rules.yaml --file tasks.org

# Custom date range
ord-plan generate --rules rules.yaml --from 2025-01-01 --to 2025-01-31 --file january.org

# Output to stdout
ord-plan generate --rules rules.yaml --from today --to next-week

# Force past date generation
ord-plan generate --rules rules.yaml --from 2024-12-01 --to 2024-12-31 --force
```
