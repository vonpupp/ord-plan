# YAML Schema Contract: Rules File

**Purpose**: Define structure and validation rules for YAML rules files

## Root Structure

```yaml
# Configuration for date tree formatting
REVERSE_DATETREE_WEEK_FORMAT: "%Y-W%V"
REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d %a"
REVERSE_DATETREE_YEAR_FORMAT: "%Y"

# Array of event definitions
events:
  - # Event object (see below)
  - # Event object
```

## Event Object Schema

### Required Fields

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `title` | string | Event title for org-mode headline | Non-empty string |
| `cron` | string | Cron expression for scheduling | Valid croniter syntax |

### Optional Fields

| Field | Type | Default | Description | Validation |
|-------|------|---------|-------------|------------|
| `tags` | array | [] | List of org-mode tags | Array of valid tag strings |
| `todo_state` | string | "TODO" | Org-mode TODO state | None |
| `description` | string | null | Multi-line event description | Text content |

## Tag Validation Rules

- Tags must be alphanumeric with hyphens and underscores
- No spaces allowed in tags
- Maximum length: 50 characters per tag
- Maximum number of tags per event: 10

## TODO State Validation
- No validation

## Description Format

- Supports multi-line text
- Preserves indentation for org-mode checkbox lists
- Maximum length: 1000 characters
- Can contain org-mode markup

## Examples

### Minimal Event
```yaml
title: "Morning Exercise"
cron: "0 7 * * 1,3,5"
```

### Full Event
```yaml
title: "Team Meeting"
cron: "0 14 * * 2"
tags: ["work", "meeting", "team"]
todo_state: "TODO"
description: |
  - [ ] Review agenda
  - [ ] Prepare updates
  - [ ] Assign action items
```

### Complete Rules File
```yaml
REVERSE_DATETREE_WEEK_FORMAT: "%Y-W%V"
REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d %a"
REVERSE_DATETREE_YEAR_FORMAT: "%Y"

events:
  - title: "Gym"
    cron: "0 0 * * 1,3,5"
    tags: ["health", "exercise"]
  - title: "Work Sprint"
    cron: "0 9 * * 1,2,3,4,5"
    todo_state: "INPROGRESS"
    tags: ["work", "development"]
    description: |
      Focus on development tasks during this time block.
      Code review and collaboration as needed.
  - title: "Weekly Review"
    cron: "0 16 * * 5"
    todo_state: "TODO"
    tags: ["work", "planning"]
    description: |
      - [ ] Review completed tasks
      - [ ] Plan next week's priorities
      - [ ] Update project documentation
```

## Extensibility

Unknown properties at root level and event level are allowed for future extensibility:
- Custom properties are ignored by current implementation
- Custom event properties are not processed but preserved for future use
- Validation only enforces required fields and formats for known properties

## Error Handling

### File-Level Errors
- Invalid YAML: Return parsing error with line number
- Missing required fields: List specific missing fields
- Invalid file structure: Provide schema location and expected format

### Event-Level Errors
- Invalid cron expression: Continue processing other events, report specific error
- Invalid tags: Strip invalid tags, continue with valid ones

### Validation Warnings
- Unknown properties: Ignore but log warning
- Deprecated field names: Suggest new field names
- Unusual cron patterns: Warn about potential issues
