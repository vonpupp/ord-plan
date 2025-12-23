# Data Model: Add Format Flag for Configuration Decoupling

**Feature**: 004-add-format-flag
**Date**: 2025-12-23
**Purpose**: Define data structures for format file configuration and merging logic

## Entities

### Format File Configuration

**Description**: YAML file containing only formatting configuration options for org-mode output generation.

**Fields**:

| Field Name | Type | Required | Default | Description |
|------------|------|----------|----------|-------------|
| REVERSE_DATETREE_YEAR_FORMAT | string | No | "%Y" | Format string for year-level headlines |
| REVERSE_DATETREE_WEEK_FORMAT | string | No | "%Y-W%V" | Format string for week-level headlines |
| REVERSE_DATETREE_DATE_FORMAT | string | No | "%Y-%m-%d %a" | Format string for date-level headlines |
| REVERSE_DATETREE_USE_WEEK_TREE | boolean | No | true | Whether to use week-based hierarchy |

**Constraints**:
- Must be valid YAML
- Field names are case-sensitive
- All values are optional (use defaults if missing)
- No `events` section allowed in format files
- Unknown keys generate warnings but don't cause errors

**Example**:
```yaml
REVERSE_DATETREE_WEEK_FORMAT: "%Y-W%V"
REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d %a"
REVERSE_DATETREE_YEAR_FORMAT: "%Y"
REVERSE_DATETREE_USE_WEEK_TREE: true
```

**Empty format file**:
```yaml
# All formatting options will use defaults
```

---

### Rules File Configuration (Combined Format)

**Description**: YAML file containing both event definitions and optional formatting options.

**Fields**:

| Field Name | Type | Required | Default | Description |
|------------|------|----------|----------|-------------|
| REVERSE_DATETREE_YEAR_FORMAT | string | Yes* | "%Y" | Format string for year-level headlines |
| REVERSE_DATETREE_DATE_FORMAT | string | Yes* | "%Y-%m-%d %a" | Format string for date-level headlines |
| REVERSE_DATETREE_WEEK_FORMAT | string | Yes* | "%Y-W%V" | Format string for week-level headlines |
| REVERSE_DATETREE_USE_WEEK_TREE | boolean | Yes* | true | Whether to use week-based hierarchy |
| events | array | Yes | - | List of event definitions |

**Constraints**:
- Must be valid YAML
- All four formatting fields are required in combined format
- `events` section is required
- Each event must have `title` and `cron` fields
- Unknown keys generate warnings but don't cause errors

**Example**:
```yaml
REVERSE_DATETREE_WEEK_FORMAT: "%Y-W%V"
REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d %a"
REVERSE_DATETREE_YEAR_FORMAT: "%Y"
REVERSE_DATETREE_USE_WEEK_TREE: true

events:
  - title: "Morning Exercise"
    cron: "0 7 * * 1,3,5"
    tags: ["health", "exercise"]
```

---

### Rules File Configuration (Events-Only Format)

**Description**: YAML file containing only event definitions, for use with separate format file.

**Fields**:

| Field Name | Type | Required | Default | Description |
|------------|------|----------|----------|-------------|
| events | array | Yes | - | List of event definitions |

**Constraints**:
- Must be valid YAML
- No formatting fields required (supplied by format file)
- Each event must have `title` and `cron` fields

**Example**:
```yaml
events:
  - title: "Morning Exercise"
    cron: "0 7 * * 1,3,5"
    tags: ["health", "exercise"]
```

---

### Merged Configuration

**Description**: Internal representation combining formatting options from format file (if provided) with events from rules file.

**Fields**: Same as Configuration dataclass in `src/ord_plan/cli/config.py`

**Merge Logic**:
1. Start with default Configuration values
2. Apply rules file formatting options (if present)
3. Apply format file formatting options (if present), overwriting rules file values
4. Apply environment variable overrides (existing behavior)

**Precedence** (highest to lowest):
1. Environment variables (existing)
2. Format file options (new)
3. Rules file options (existing)
4. Configuration defaults (existing)

**State Transitions**:

```
Empty rules file + empty format file → All defaults
Combined rules file → Rules formatting used
Format file + events-only rules file → Format formatting used
Format file + combined rules file → Format formatting used (precedence)
```

---

### Event Rule

**Description**: Single event definition (existing entity, unchanged).

**Fields**:

| Field Name | Type | Required | Default | Description |
|------------|------|----------|----------|-------------|
| title | string | Yes | - | Event title/headline text |
| cron | string | Yes | - | Cron expression for scheduling |
| tags | array | No | [] | List of tags for categorization |
| todo_state | string | No | "TODO" | Org-mode TODO keyword |
| description | string | No | - | Short description |
| body | string | No | - | Multi-line body content |

**Constraints**:
- Title max 200 characters
- Tags max 10 items, each max 50 characters, no spaces
- Todo state max 20 characters
- Description max 1000 characters
- Body max 5000 characters

---

## Relationships

```
Format File (optional)
     ↓
Merged Configuration ← Rules File (required)
     ↓                         ↓
     └─────────→ Event Rules ←┘
                       ↓
                 Generated Org Output
```

## Validation Rules

### Format File Validation

1. **YAML Syntax**: Must be valid YAML
2. **Structure**: Must be dictionary/object at root
3. **Allowed Keys**:
   - REVERSE_DATETREE_YEAR_FORMAT
   - REVERSE_DATETREE_WEEK_FORMAT
   - REVERSE_DATETREE_DATE_FORMAT
   - REVERSE_DATETREE_USE_WEEK_TREE
4. **Forbidden Keys**: `events` section not allowed
5. **Date Format Validation**: Each format string must be valid for `datetime.strftime()`

### Rules File Validation

1. **YAML Syntax**: Must be valid YAML
2. **Structure**: Must be dictionary/object at root
3. **Events Section**: Required
4. **Event Fields**: Each event must have `title` and `cron`

### Merged Configuration Validation

1. **Date Formats**: All format strings must be valid for `datetime.strftime()`
2. **Boolean Parsing**: REVERSE_DATETREE_USE_WEEK_TREE must parse as boolean
3. **Type Safety**: All fields must match expected types

## Error Handling

### Format File Errors

| Error Condition | Error Type | User Message |
|----------------|-------------|---------------|
| File not found | Click Abort | "Error: Format file {path} does not exist" |
| File not readable | Click Abort | "Error: Format file {path} is not readable" |
| Invalid YAML | Click Abort | "YAML parsing error: {details}" |
| Invalid date format | Click Abort | "Configuration errors: {format} is invalid: {details}" |
| Unknown key | Warning (stderr) | "Warning: Unknown configuration key {key} will be ignored" |
| Events section present | Error | "Error: Format file must not contain 'events' section" |

### Rules File Errors

| Error Condition | Error Type | User Message |
|----------------|-------------|---------------|
| Missing required formatting fields | Error | "Missing mandatory header variable: {field}" |
| Invalid YAML | Click Abort | "YAML parsing error: {details}" |
| Invalid cron expression | Click Abort | "Cron expression validation errors: {details}" |

### Merge Errors

| Error Condition | Error Type | User Message |
|----------------|-------------|---------------|
| Conflicting boolean values | Warning | "Warning: Conflicting boolean value for {key}, using format file value" |

## Data Lifecycle

1. **Load**: Parse YAML files into dictionaries
2. **Validate**: Check YAML syntax and schema
3. **Merge**: Combine format and rules configurations with precedence
4. **Create**: Instantiate Configuration dataclass
5. **Use**: Pass to EventService for org-mode generation
6. **Discard**: Configuration is short-lived, not persisted
