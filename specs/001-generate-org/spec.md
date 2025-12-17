# Feature Specification: Generate Org Events from Cron Rules

**Feature Branch**: `001-generate-org`
**Created**: 2025-12-16
**Status**: Draft
**Input**: User description: "For this tool I want to use the python packages croniter, orgparse and pyyaml.

This is an example of the generate command:
```
ord-plan generate --rules expanded_rules.yaml --file ~/org/tasks.org
```

Explanation:
- The rules file is a yaml file, I will exemplify later.
- The from flag is the beginning date of the generated events (optional)
- The to flag is the end date of the generated events (optional)
- When from and too flags don't exist the default logic is to generate events for next week (from monday to sunday)
- The file flag is the file where the events will be generated. The data on the file must be preserved, no data loss should ever happen, just data aggregation. This flag is also optional, if it is not provided the output should be stdout

Cooincidentally the following command if executed on the 2025-12-14 without providing any "from" or "to" flag, should generate the same output. I will show the expected output later
```
ord-plan generate --rules expanded_rules.yaml --from 2025-12-14 --to 2025-12-21 --file ~/org/tasks.org
```
cat expanded_rules.yaml
---
REVERSE_DATETREE_WEEK_FORMAT: "%Y-W%W"
REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d %a"
REVERSE_DATETREE_YEAR_FORMAT: "%Y"
events:
  - title: "Gym"
    cron: "0 0 * * 1,3,5"
    tags: ["health", "gym"]
  - title: "Coding"
    cron: "0 0 * * 1,2,3,4,5,7"
    tags: ["skills", "code", "project"]
  - title: "Music learning"
    cron: "0 0 * * 1,2,3,4,5,6"
    tags: ["learn", "music", "project"]
  - title: "Music composition"
    cron: "0 0 * * 6,0"
    tags: ["learn", "music", "project"]
  - title: "DSI"
    cron: "0 0 * * 0"  # All-day event on Sundays
    todo_state: "TODO"
    tags: ["family"]
    description: |
      - [ ] Planning time
      - [ ] What went fine
      - [ ] What went wrong
      - [ ] What can be improved
  - title: "Date night"
    cron: "0 0 * * 4"
    tags: ["family"]

cat ~/org/tasks.org
* 2025
** 2025-W50
*** 2025-12-21 Sun
**** TODO Coding                                      :skill:code:project:
**** TODO Music composition                                  :learn:music:
**** TODO DSI                                                     :family:
- [ ] Planning time
- [ ] What went fine
- [ ] What went wrong
- [ ] What can be improved
***  2025-12-20 Sat
**** TODO Music learning                                     :learn:music:
**** TODO Music composition                                  :learn:music:
***  2025-12-19 Fri
**** TODO Gym                                                 :health:gym:
**** TODO Coding                                      :skill:code:project:
**** TODO Music learning                                     :learn:music:
***  2025-12-18 Thu
**** TODO Coding                                      :skill:code:project:
**** TODO Music learning                                     :learn:music:
**** TODO Date night                                              :family:
**** TODO APPOINTMENT Dentist                                     :health:
***  2025-12-17 Wed
**** TODO Gym                                                 :health:gym:
**** TODO Coding                                      :skill:code:project:
**** TODO Music learning                                     :learn:music:
***  2025-12-16 Tue
**** TODO Coding                                      :skill:code:project:
**** TODO Music learning                                     :learn:music:
***  2025-12-15 Mon
**** TODO Coding                                      :skill:code:project:
**** TODO Music learning                                     :learn:music:
*** 2025-12-14 Sun
**** TODO Coding                                      :skill:code:project:
**** TODO Music composition                                  :learn:music:
**** TODO DSI                                                     :family:
- [ ] Planning time
- [ ] What went fine
- [ ] What went wrong
- [ ] What can be improved
... File continues with previous entries that should not be modified

Notice that on thursday there was already a dentist appointment. The system will just aggregate the tasks of that day, preserving the existing task.

Use these outputs as fixtures to test the app before even implementing the generate command feature.

Some edge cases:
- If the cron expression is broken, the app must trough an exception.
- If on that day there are events already, the events are kept. Regardless if they look repeated. You must NEVER delete data from the file.
- If the cron expression doesn't produce any events, just don't produce any events. The user will have to figure it out.
- If the target org file doesn't exists, create the file.
- If data is in the past you must warn the user. You must have a "--force" flag to confirm that this is really what the user wants. Same for something far in the future (more than 1 year)."

## Clarifications

### Session 2025-12-16
- Q: How should the system handle events with identical titles, dates, and times? → A: Treat events with same title/date/time as separate entries, never deduplicate
- Q: How should YAML configuration schema validation work? → A: Validate required fields but allow unknown properties for extensibility




## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Event Generation (Priority: P1)

As a user, I want to generate org-mode events from cron-based rules so that I can create structured task schedules automatically.

**Why this priority**: This is the core functionality that delivers the primary value of the tool - converting time-based rules into org-mode format.

**Independent Test**: Can be fully tested by generating events for a specific date range and verifying the output format matches expected org-mode structure.

**Acceptance Scenarios**:

1. **Given** a valid YAML rules file with cron expressions, **When** I run the generate command with a specific date range, **Then** events are generated in proper org-mode format with correct hierarchical structure
2. **Given** a rules file with multiple events, **When** I generate events for a week, **Then** all matching events appear under the correct date headings with appropriate tags and properties

---

### User Story 2 - Date Range Flexibility (Priority: P1)

As a user, I want to specify custom date ranges or use defaults so that I can generate events for any time period I need.

**Why this priority**: Flexibility in date selection is essential for practical usage - users need to plan ahead, review past periods, or use the common default of next week.

**Independent Test**: Can be fully tested by running the command with different date combinations and verifying the correct date ranges are processed.

**Acceptance Scenarios**:

1. **Given** no date flags specified, **When** I run the generate command on any day, **Then** events are generated for the upcoming Monday to Sunday
2. **Given** specific from/to dates, **When** I run the generate command, **Then** events are generated only for the specified date range inclusive
3. **Given** from/to dates without a file flag, **When** I run the generate command, **Then** events are output to stdout instead of a file

---

### User Story 3 - File Preservation and Safety (Priority: P1)

As a user, I want existing org-mode content to be preserved so that I can safely add generated events without losing any existing data.

**Why this priority**: Data safety is critical - users must trust that the tool will not delete or modify their existing org-mode entries.

**Independent Test**: Can be fully tested by generating events into a file with existing content and verifying all original entries remain unchanged.

**Acceptance Scenarios**:

1. **Given** an existing org file with entries, **When** I generate new events for dates that already have content, **Then** existing entries are preserved and new events are appended
2. **Given** a non-existent target file path, **When** I run the generate command, **Then** a new file is created with the generated events

---

### User Story 4 - Error Handling and Validation (Priority: P2)

As a user, I want clear error messages and validation so that I can understand and fix configuration issues quickly.

**Why this priority**: Good error handling prevents user frustration and helps users identify problems with their rules or configuration.

**Independent Test**: Can be fully tested by providing invalid inputs and verifying appropriate error handling.

**Acceptance Scenarios**:

1. **Given** a rules file with invalid cron expressions, **When** I run the generate command, **Then** the system exits with a clear error message indicating the problematic cron expression
2. **Given** a non-existent rules file, **When** I run the generate command, **Then** the system exits with a clear file not found error

---

### User Story 5 - Date Protection and Warnings (Priority: P2)

As a user, I want warnings when generating events for past dates or far future dates so that I can confirm these intentional actions.

**Why this priority**: Prevents accidental data generation for inappropriate time ranges while still allowing intentional use cases.

**Independent Test**: Can be fully tested by attempting to generate events for past dates and far future dates with and without the force flag.

**Acceptance Scenarios**:

1. **Given** a date range including past dates without --force, **When** I run the generate command, **Then** the system warns about past date generation and requires confirmation
2. **Given** a date range extending more than 1 year in the future without --force, **When** I run the generate command, **Then** the system warns about far future dates and requires confirmation
3. **Given** any date range with --force flag, **When** I run the generate command, **Then** events are generated without warnings

---

### Edge Cases

- What happens when cron expressions don't match any dates in the specified range? System should generate no events and continue without error
- How does system handle malformed YAML rules files? System should exit with clear parsing error
- What happens when target org file has invalid formatting? System should attempt to preserve existing structure and add new content
- How does system handle concurrent access? System relies on filesystem permissions, no special concurrent access handling
- How does system handle events with identical titles and dates? System treats them as separate entries and never deduplicates
- What happens when timezone is not specified? System should use system local timezone

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide CLI command "generate" with flags --rules (required), --file (optional), --from (optional), --to (optional), --force (optional)
- **FR-002**: System MUST parse YAML rules files containing cron expressions, event properties, and formatting configuration with validation of required fields while allowing unknown properties for extensibility
- **FR-003**: System MUST use croniter to process cron expressions and generate event occurrences within date ranges
- **FR-004**: System MUST generate org-mode output following hierarchical date tree structure (year > week > date > events)
- **FR-005**: System MUST preserve all existing content in target org files without modification
- **FR-006**: System MUST support configurable date formats for tree structure via YAML configuration
- **FR-007**: System MUST validate cron expressions and exit with error for invalid expressions
- **FR-008**: System MUST default to next week (Monday to Sunday) when no date range is specified
- **FR-009**: System MUST output to stdout when no --file flag is provided
- **FR-010**: System MUST create new files when target file doesn't exist
- **FR-011**: System MUST warn for past date ranges and require --force flag for confirmation
- **FR-012**: System MUST warn for future date ranges beyond 1 year and require --force flag for confirmation
- **FR-013**: System MUST support orgparse for reading and writing org-mode format
- **FR-014**: System MUST handle events with todo states, tags, descriptions, and titles
- **FR-015**: System MUST aggregate events by date without deleting existing entries

### Key Entities *(include if feature involves data)*

- **Event Rule**: Represents a recurring event with title, cron expression, tags, todo state, and description
- **Date Range**: Defines the start and end dates for event generation with validation for past/future ranges
- **Org File Structure**: Hierarchical organization of years, weeks, dates, and individual events with preserved existing content
- **Configuration**: YAML-based formatting rules for date structures and output patterns

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: CLI command completes event generation in under 30 seconds for schedules with up to 1000 events
- **SC-002**: System processes YAML rules files up to 50KB without performance degradation while maintaining 50% test coverage
- **SC-003**: 100% of existing org file content is preserved during event aggregation operations
- **SC-004**: All generated org-mode output validates successfully against org-mode parser standards
- **SC-005**: Error handling provides clear, actionable messages for 100% of invalid input scenarios
- **SC-006**: Date range warnings correctly trigger for past dates and future dates beyond 1 year
- **SC-007**: Default date range generates events for current Monday to Sunday regardless of execution day
- **SC-008**: Cron expression validation prevents generation from malformed time patterns
