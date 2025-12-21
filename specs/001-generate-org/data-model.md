# Data Model: Generate Org Events from Cron Rules

**Date**: 2025-12-16
**Feature**: 001-generate-org

## Core Entities

### EventRule

Represents a recurring event definition from YAML configuration.

**Fields**:

- `title: str` - Event title (required)
- `cron: str` - Cron expression for scheduling (required)
- `tags: List[str]` - Event tags (optional, default: [])
- `todo_state: str` - TODO state for org-mode (optional, default: None)
- `description: str` - Multi-line event description (optional, default: None)

**Validation Rules**:

- Title cannot be empty
- Cron expression must be valid croniter format
- Tags must be valid org-mode tag format (no spaces, alphanumeric with hyphens/underscores)

### DateRange

Defines the time period for event generation.

**Fields**:

- `start_date: datetime` - Inclusive start date
- `end_date: datetime` - Inclusive end date
- `warnings: List[str]` - Collected warnings during validation

**Validation Rules**:

- Start date must be <= end date
- Past dates trigger warning unless force flag used
- Future dates beyond 1 year trigger warning unless force flag used

### OrgDateNode

Represents a date node in the org-mode hierarchy.

**Fields**:

- `date: datetime` - The date this node represents
- `year: str` - Formatted year string
- `week: str` - Formatted week string
- `day: str` - Formatted day string
- `existing_events: List[OrgEvent]` - Events already in target file
- `new_events: List[OrgEvent]` - Events to be added

### OrgEvent

Represents a single org-mode event.

**Fields**:

- `title: str` - Event title
- `todo_state: Optional[str]` - TODO state
- `tags: List[str]` - Event tags
- `description: Optional[str]` - Multi-line description
- `level: int` - Org-mode headline level (default: 4 for events)

### Configuration

Represents the formatting and behavior configuration.

**Fields**:

- `reverse_datetree_year_format: str` - Year formatting template
- `reverse_datetree_week_format: str` - Week formatting template
- `reverse_datetree_date_format: str` - Date formatting template
- `default_todo_state: str` - Default TODO state for events without explicit state

**Default Values**:

- Year format: "%Y"
- Week format: "%Y-W%V"
- Date format: "%Y-%m-%d %a"
- Default TODO state: "TODO"

## Relationships

```
EventRule --(generates)--> OrgEvent
OrgEvent --(belongs to)--> OrgDateNode
DateRange --(filters)--> OrgEvent
Configuration --(formats)--> OrgDateNode
```

## State Transitions

### File Processing State

1. **Initial** - Target file analysis
2. **Parsing** - Reading existing org-mode content
3. **Generation** - Creating new events from rules
4. **Merging** - Combining existing and new events
5. **Writing** - Outputting final org-mode content

### Validation State

1. **Schema Validation** - YAML structure and required fields
2. **Cron Validation** - Cron expression syntax
3. **Date Validation** - Date range and warning checks
4. **File Validation** - Target file permissions and accessibility

## Data Flow

```
YAML Rules → EventRule[] → Cron Matching → OrgEvent[] → Date Grouping → OrgDateNode[] → Merge with Existing → Final Org Content
```

## Invariants

- All generated events must have valid dates within the specified range
- Existing org-mode content must be preserved exactly
- All new events must follow org-mode formatting standards
- Date hierarchy must be maintained (year > week > date > events)
- No two events can be identical based on title, date, and time
