# Tasks: Add Format Flag for Configuration Decoupling

**Input**: Design documents from `/specs/004-add-format-flag/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: This feature requires TDD with 100% test coverage (per constitution check).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **CLI Tool**: `src/ord_plan/`, `tests/` at repository root
- Paths shown below follow the CLI tool structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create test fixtures directory structure for format files in tests/fixtures/
- [X] T002 [P] Review existing code structure in src/ord_plan/cli/, src/ord_plan/parsers/
- [X] T003 [P] Verify existing test infrastructure in tests/contract/, tests/integration/, tests/unit/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add parse_format_file() method in src/ord_plan/parsers/yaml_parser.py
- [X] T005 [P] Add validate_format_schema() method in src/ord_plan/parsers/yaml_parser.py [P]
- [X] T006 [P] Add merge_format_config() class method in src/ord_plan/cli/config.py [P]
- [X] T007 Add --format parameter to generate() command in src/ord_plan/cli/generate.py
- [X] T008 Implement format file parsing and merging logic in generate() command handler

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Separate Format Configuration (Priority: P1) 🎯 MVP

**Goal**: Enable users to separate formatting configuration from event rules by using a separate format file with the --format flag.

**Independent Test**: Create a format file with formatting options and a rules file with events, run the generate command with both flags, and verify the output matches the expected org-mode structure with correct formatting applied.

### Tests for User Story 1 (MANDATORY - TDD requirement) ⚠️

> **CRITICAL: Write these tests FIRST, ensure they FAIL before implementation (TDD requirement)**

- [X] T009 [P] [US1] Contract test: --format flag validation in tests/contract/test_generate_command.py
- [X] T010 [P] [US1] Contract test: format file not found error in tests/contract/test_generate_command.py
- [X] T011 [P] [US1] Integration test: separate format and rules files in tests/integration/test_format_flag.py
- [X] T012 [P] [US1] Unit test: parse_format_file() with valid format file in tests/unit/test_parsers/test_yaml_parser.py
- [X] T013 [P] [US1] Unit test: parse_format_file() with empty format file in tests/unit/test_parsers/test_yaml_parser.py
- [X] T014 [P] [US1] Unit test: parse_format_file() with invalid YAML in tests/unit/test_parsers/test_yaml_parser.py
- [X] T015 [P] [US1] Unit test: merge_format_config() with format and rules in tests/unit/test_cli/test_config.py
- [X] T016 [P] [US1] Unit test: validate_format_schema() with events section error in tests/unit/test_parsers/test_yaml_parser.py

### Implementation for User Story 1

- [X] T017 [P] [US1] Implement parse_format_file() in src/ord_plan/parsers/yaml_parser.py
- [X] T018 [P] [US1] Implement validate_format_schema() in src/ord_plan/parsers/yaml_parser.py
- [X] T019 [US1] Implement merge_format_config() in src/ord_plan/cli/config.py
- [X] T020 [US1] Add --format parameter to generate() command in src/ord_plan/cli/generate.py
- [X] T021 [US1] Implement format file parsing and configuration merging in generate() command in src/ord_plan/cli/generate.py
- [X] T022 [US1] Add error handling for format file validation errors in src/ord_plan/cli/generate.py
- [X] T023 [US1] Add test fixtures for valid format file in tests/fixtures/test_format_valid.yaml
- [X] T024 [US1] Add test fixtures for empty format file in tests/fixtures/test_format_empty.yaml
- [X] T025 [US1] Add test fixtures for events-only rules file in tests/fixtures/test_rules_events_only.yaml
- [X] T026 [US1] Update CLI help documentation for --format flag in src/ord_plan/cli/generate.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Backward Compatibility (Priority: P2)

**Goal**: Ensure existing combined rules files (with formatting + events) continue to work without modifications when no --format flag is provided.

**Independent Test**: Run the generate command with an existing combined rules file and verify the output matches the expected behavior from before this feature was added.

### Tests for User Story 2 (MANDATORY - TDD requirement) ⚠️

- [X] T027 [P] [US2] Integration test: combined rules file without --format flag in tests/integration/test_backward_compat.py
- [X] T028 [P] [US2] Integration test: events-only rules file without --format flag in tests/integration/test_backward_compat.py
- [X] T029 [P] [US2] Integration test: existing workflow unchanged in tests/integration/test_backward_compat.py

### Implementation for User Story 2

- [X] T030 [US2] Verify existing combined rules file parsing in src/ord_plan/parsers/yaml_parser.py
- [X] T031 [US2] Verify default configuration fallback in src/ord_plan/cli/config.py
- [X] T032 [US2] Ensure no breaking changes to existing command behavior in src/ord_plan/cli/generate.py
- [X] T033 [US2] Run existing test suite to verify no regressions

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Format File Override (Priority: P3)

**Goal**: When both format file and rules file define the same formatting option, the format file's value takes precedence.

**Independent Test**: Create a format file with one setting and a rules file with a conflicting setting, run generate with both flags, and verify the output uses the format file's setting.

### Tests for User Story 3 (MANDATORY - TDD requirement) ⚠️

- [X] T034 [P] [US3] Unit test: format file overrides rules file in tests/unit/test_cli/test_config.py
- [X] T035 [P] [US3] Integration test: conflicting date formats in tests/integration/test_format_override.py
- [X] T036 [P] [US3] Integration test: partial format file overrides specific options in tests/integration/test_format_override.py
- [X] T037 [P] [US3] Integration test: precedence order (format > rules > defaults) in tests/integration/test_format_override.py

### Implementation for User Story 3

- [X] T038 [US3] Verify format file precedence in merge_format_config() in src/ord_plan/cli/config.py
- [X] T039 [US3] Add test fixtures for format override scenario in tests/fixtures/test_format_override.yaml
- [X] T040 [US3] Add test fixtures for conflicting rules file in tests/fixtures/test_rules_conflicting.yaml
- [X] T041 [US3] Add test fixtures for partial format file in tests/fixtures/test_format_partial.yaml

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Edge Case Handling (Cross-Cutting)

**Purpose**: Ensure robust handling of edge cases and error conditions

### Tests for Edge Cases (MANDATORY - TDD requirement) ⚠️

- [X] T042 [P] Unit test: invalid date format in format file in tests/unit/test_parsers/test_yaml_parser.py
- [X] T043 [P] Unit test: unknown configuration key warning in tests/unit/test_parsers/test_yaml_parser.py
- [X] T044 [P] Unit test: duplicate formatting keys in format file in tests/unit/test_parsers/test_yaml_parser.py
- [X] T045 [P] Unit test: invalid boolean value for week tree in tests/unit/test_parsers/test_yaml_parser.py
- [X] T046 [P] Unit test: events section in format file error in tests/unit/test_parsers/test_yaml_parser.py
- [X] T047 [P] Integration test: format file with all defaults in tests/integration/test_edge_cases.py
- [X] T048 [P] Integration test: format and rules both missing formatting in tests/integration/test_edge_cases.py

### Implementation for Edge Cases

- [X] T049 Add validation for invalid date format strings in src/ord_plan/parsers/yaml_parser.py
- [X] T050 Add warning for unknown configuration keys in src/ord_plan/parsers/yaml_parser.py
- [X] T051 Add handling for duplicate keys in format file in src/ord_plan/parsers/yaml_parser.py
- [X] T052 Add validation for boolean parsing in src/ord_plan/parsers/yaml_parser.py
- [X] T053 Add check for forbidden events section in format file in src/ord_plan/parsers/yaml_parser.py
- [X] T054 Add test fixtures for invalid date format in tests/fixtures/test_format_invalid_date.yaml
- [X] T055 Add test fixtures for unknown keys in tests/fixtures/test_format_unknown_key.yaml
- [X] T056 Add test fixtures for invalid boolean in tests/fixtures/test_format_invalid_bool.yaml
- [X] T057 Add test fixtures for events section in format file in tests/fixtures/test_format_with_events.yaml

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T058 [P] Update CLI help text and examples in docs/usage.md
- [X] T059 [P] Update quickstart.md with migration examples in specs/004-add-format-flag/quickstart.md
- [X] T060 Run full test suite with coverage to ensure 100% coverage for new code paths
- [X] T061 Run linting (invoke lint) and fix any issues
- [X] T062 Verify all quickstart.md examples work end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Edge Cases (Phase 6)**: Depends on User Stories 1, 2, 3 completion
- **Polish (Phase 7)**: Depends on all user stories and edge cases being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Should verify no regressions from US1
- **User Story 3 (P3)**: Can start after User Story 1 (depends on merge_format_config() implementation)

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD requirement)
- Model/service methods before CLI integration
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, User Stories 1 and 2 can start in parallel
- All tests for a user story marked [P] can run in parallel
- Edge case tests marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD - write first, ensure they fail):
Task: "T009 [P] [US1] Contract test: --format flag validation in tests/contract/test_generate_command.py"
Task: "T010 [P] [US1] Contract test: format file not found error in tests/contract/test_generate_command.py"
Task: "T011 [P] [US1] Integration test: separate format and rules files in tests/integration/test_format_flag.py"
Task: "T012 [P] [US1] Unit test: parse_format_file() with valid format file in tests/unit/test_parsers/test_yaml_parser.py"
Task: "T013 [P] [US1] Unit test: parse_format_file() with empty format file in tests/unit/test_parsers/test_yaml_parser.py"

# Launch parallel implementation tasks after tests fail:
Task: "T017 [P] [US1] Implement parse_format_file() in src/ord_plan/parsers/yaml_parser.py"
Task: "T018 [P] [US1] Implement validate_format_schema() in src/ord_plan/parsers/yaml_parser.py"
Task: "T019 [US1] Implement merge_format_config() in src/ord_plan/cli/config.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently with quickstart.md examples
5. Verify all tests pass with 100% coverage for new code paths
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Validate with quickstart.md examples → MVP ready!
3. Add User Story 2 → Test independently → Ensure no regressions
4. Add User Story 3 → Test independently → Verify precedence rules
5. Add Edge Cases → Test all error conditions
6. Each increment adds value without breaking previous functionality

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (MVP focus)
   - Developer B: User Story 2 (backward compatibility)
   - Developer C: User Story 3 (format override) after US1 foundation exists
3. Developer D: Edge Cases after core stories complete
4. All integrate independently with minimal coordination

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **TDD is MANDATORY**: Verify tests fail before implementing
- Run `invoke pytest` after each task or logical group
- Run `invoke lint` after implementation complete
- Stop at any checkpoint to validate story independently
- Verify quickstart.md examples work before marking complete
- Ensure 100% test coverage for all new code paths (per constitution)
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
