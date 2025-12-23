# Feature Specification: Add Format Flag for Configuration Decoupling

**Feature Branch**: `001-add-format-flag`
**Created**: 2025-12-23
**Status**: Draft
**Input**: User description: "I want to refactor the app so the rules do not deal with formatting, but rather add a new flag."

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Separate Format Configuration (Priority: P1)

A user wants to separate their formatting configuration from their event rules for better reusability and maintainability. They create a format file with only formatting options (date formats, week formats, tree settings) and a separate rules file with event definitions. The tool merges these files to generate org-mode output.

**Why this priority**: This is the core functionality requested by the user and provides immediate value by enabling configuration reuse and cleaner separation of concerns.

**Independent Test**: Can be fully tested by creating a format file with formatting options and a rules file with events, running the generate command with both flags, and verifying the output matches the expected org-mode structure with correct formatting applied.

**Acceptance Scenarios**:

1. **Given** a format file with `REVERSE_DATETREE_WEEK_FORMAT: "%Y-W%V"`, `REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d %a"`, `REVERSE_DATETREE_YEAR_FORMAT: "%Y"`, and `REVERSE_DATETREE_USE_WEEK_TREE: true`, **When** the user runs `ord-plan generate --format <format-file> --rules <rules-file> --from <date> --to <date>`, **Then** the output uses the specified formats for year, week, and date levels, and generates a week-based tree structure.

2. **Given** a format file with only some formatting options defined (e.g., missing `REVERSE_DATETREE_WEEK_FORMAT`), **When** the user runs generate with both format and rules files, **Then** the tool applies the defined options and uses reasonable defaults for undefined options.

3. **Given** a rules file containing only an `events` list with no formatting headers, **When** combined with a format file via the `--format` flag, **Then** the tool generates correct output using formatting from the format file and events from the rules file.

---

### User Story 2 - Backward Compatibility (Priority: P2)

A user wants to continue using existing rules files that contain both formatting options and events (the combined format). The tool should still work correctly with these files even after the new format flag is added.

**Why this priority**: Ensuring backward compatibility prevents breaking existing workflows and allows users to adopt the new approach at their own pace.

**Independent Test**: Can be tested by running the generate command with an existing combined rules file (one that has formatting headers and events) and verifying the output matches the expected behavior from before this feature was added.

**Acceptance Scenarios**:

1. **Given** a combined rules file with formatting headers and events, **When** the user runs `ord-plan generate --rules <rules-file> --from <date> --to <date>` without specifying `--format`, **Then** the tool uses the formatting options from the rules file and generates correct output.

2. **Given** an existing workflow using combined rules files, **When** the user upgrades to the new version, **Then** all existing commands continue to work without modifications.

---

### User Story 3 - Format File Override (Priority: P3)

A user provides both a format file and a rules file where the rules file also contains some formatting options. The format file options should take precedence over rules file options when conflicts occur.

**Why this priority**: This provides flexibility for users who want to base configurations on existing templates but customize specific formatting options.

**Independent Test**: Can be tested by creating a format file with one setting (e.g., `REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d"`), a rules file with a conflicting setting (e.g., `REVERSE_DATETREE_DATE_FORMAT: "%d/%m/%Y"`), and verifying the output uses the format file's setting.

**Acceptance Scenarios**:

1. **Given** a format file with `REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d"` and a rules file with `REVERSE_DATETREE_DATE_FORMAT: "%d/%m/%Y"`, **When** the user runs generate with both flags, **Then** the output uses `"%Y-%m-%d"` from the format file.

2. **Given** a format file with only `REVERSE_DATETREE_YEAR_FORMAT` defined and a rules file with other formatting options, **When** the user runs generate with both flags, **Then** the year format comes from the format file and other options come from the rules file.

---

### Edge Cases

- What happens when the format file is empty or contains invalid YAML?
- What happens when the format file specifies an unknown or invalid formatting key?
- How does the system handle when neither format file nor rules file provides required formatting options?
- What happens when the format file path is invalid or the file cannot be read?
- How does the system behave when the same formatting option appears multiple times within the format file?

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The tool MUST support a new `--format` command-line flag that accepts a file path to a YAML format configuration file.

- **FR-002**: The format file MUST contain only formatting configuration options (e.g., `REVERSE_DATETREE_WEEK_FORMAT`, `REVERSE_DATETREE_DATE_FORMAT`, `REVERSE_DATETREE_YEAR_FORMAT`, `REVERSE_DATETREE_USE_WEEK_TREE`).

- **FR-003**: The tool MUST internally merge formatting options from the format file with event definitions from the rules file when both are specified.

- **FR-004**: When both format file and rules file define the same formatting option, the format file's value MUST take precedence.

- **FR-005**: The tool MUST maintain backward compatibility with existing rules files that contain both formatting options and events.

- **FR-006**: When no `--format` flag is provided, the tool MUST use formatting options from the rules file if present, or use reasonable defaults if not present.

- **FR-007**: The tool MUST provide a clear error message when the format file cannot be read or contains invalid YAML.

- **FR-008**: The `--format` flag MUST be optional (not required) to maintain backward compatibility.

- **FR-009**: The tool MUST support using format files independently of rules files (format file can be reused with different rules files).

- **FR-010**: The tool MUST generate identical output for the same logical configuration whether using a combined rules file or separate format and rules files.

- **FR-011**: The tool MUST validate that formatting options in the format file are recognized and supported.

### Key Entities

- **Format Configuration File**: A YAML file containing only formatting options for org-mode output (date formats, week formats, year formats, tree settings). Does not contain event definitions.

- **Rules File**: A YAML file containing event definitions (title, cron, tags, body). May optionally contain formatting options for backward compatibility.

- **Formatting Options**: Configuration settings that control how dates and hierarchical structures are formatted in the org-mode output (e.g., `REVERSE_DATETREE_WEEK_FORMAT`, `REVERSE_DATETREE_DATE_FORMAT`, `REVERSE_DATETREE_YEAR_FORMAT`, `REVERSE_DATETREE_USE_WEEK_TREE`).

- **Merged Configuration**: The internal representation combining formatting from the format file (if provided) with events from the rules file, used to generate the org-mode output.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: Users can successfully generate org-mode output using a separate format configuration file with the `--format` flag.

- **SC-002**: Output generated using separate format and rules files is byte-for-byte identical to output generated using a combined rules file with the same logical configuration.

- **SC-003**: Existing commands and workflows that use combined rules files continue to work without any modifications after this feature is added.

- **SC-004**: When format file and rules file contain conflicting formatting options, the format file options are consistently used in the output.

- **SC-005**: Clear error messages are displayed when format files are missing, unreadable, or contain invalid YAML syntax.

- **SC-006**: The `--format` flag is properly documented in the CLI help system with examples of usage.

- **SC-007**: Format files can be reused across multiple different rules files to generate outputs with consistent formatting.

- **SC-008**: All tests pass for the new format flag functionality, including edge cases for empty files, invalid files, and merging scenarios.

## Assumptions

- Format files use YAML format, consistent with existing rules files.
- The set of supported formatting keys remains the same as currently used in rules files (no new or removed formatting options).
- Users understand the precedence rules (format file > rules file) when both define the same formatting option.
- Default values for missing formatting options are already defined and used by the tool.
- The tool's YAML parsing and error handling infrastructure is sufficient for handling format files.

## Out of Scope

- Adding new formatting options or changing the behavior of existing formatting options.
- Modifying the org-mode output structure itself (only the configuration mechanism changes).
- Supporting format file formats other than YAML.
- Providing a format file validation command separate from the generate command.
- Migration tools or utilities for converting existing combined rules files into separate format and rules files.
