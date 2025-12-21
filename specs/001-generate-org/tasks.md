# Implementation Tasks: Generate Org Events from Cron Rules

**Branch**: 001-generate-org | **Date**: 2025-12-16
**Status**: Draft
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Summary

This task breakdown implements a CLI tool that generates org-mode events from cron-based YAML rules while preserving existing file content. Tasks are organized by user stories to enable independent implementation and testing, following the project structure defined in the implementation plan.

## Phase 1: Setup

- [x] T001 Create project structure per implementation plan
- [x] T002 Set up Poetry with required dependencies (Click>=8.0.1, croniter, orgparse, PyYAML)
- [x] T003 Configure pre-commit hooks (Black, mypy, flake8)
- [x] T004 Set up pytest configuration with coverage requirements
- [x] T005 Create basic CLI entry point in src/ord_plan/**main**.py

## Phase 2: Foundational

- [x] T006 Create CLI command structure in src/ord_plan/cli/**init**.py
- [x] T007 Implement configuration handling in src/ord_plan/cli/config.py
- [x] T008 Create utility validators in src/ord_plan/utils/validators.py
- [x] T009 [P] Set up org-mode parser in src/ord_plan/parsers/org_mode.py
- [x] T010 [P] Create YAML rules parser in src/ord_plan/parsers/yaml_parser.py

## Phase 3: User Story 1 - Basic Event Generation (Priority: P1)

**Goal**: Generate org-mode events from cron-based rules so that users can create structured task schedules automatically
**Independent Test**: Generate events for specific date range and verify output format matches expected org-mode structure

- [x] T011 [US1] Create EventRule dataclass in src/ord_plan/models/event_rule.py
- [x] T012 [US1] Create DateRange dataclass in src/ord_plan/models/date_range.py
- [x] T013 [US1] Create OrgEvent dataclass in src/ord_plan/models/org_event.py
- [x] T014 [US1] Create OrgDateNode dataclass in src/ord_plan/models/org_date_node.py
- [x] T015 [P] [US1] Implement cron expression processing using croniter in src/ord_plan/services/cron_service.py
- [x] T016 [US1] Create event generation service in src/ord_plan/services/event_service.py
- [x] T017 [P] [US1] Implement org-mode renderer in src/ord_plan/parsers/org_mode.py
- [x] T018 [US1] Create main generate command in src/ord_plan/cli/generate.py
- [x] T019 [US1] Integrate generate command with CLI in src/ord_plan/cli/**init**.py
- [x] T020 [US1] Add end-to-end test for basic event generation in tests/integration/test_basic_generation.py

## Phase 4: User Story 2 - Date Range Flexibility (Priority: P1)

**Goal**: Specify custom date ranges or use defaults so users can generate events for any time period
**Independent Test**: Run command with different date combinations and verify correct date ranges are processed

- [x] T021 [P] [US2] Implement date range validation in src/ord_plan/services/date_service.py
- [x] T022 [US2] Add relative date parsing ("today", "next monday") in src/ord_plan/services/date_service.py
- [x] T023 [US2] Implement default date range logic (Monday to Sunday) in src/ord_plan/cli/generate.py
- [x] T024 [US2] Add --from and --to parameter handling in src/ord_plan/cli/generate.py
- [x] T025 [US2] Create date range tests in tests/unit/test_date_service.py
- [x] T026 [P] [US2] Add integration test for date range flexibility in tests/integration/test_date_ranges.py

## Phase 5: User Story 3 - File Preservation and Safety (Priority: P1)

**Goal**: Existing org-mode content is preserved so users can safely add generated events without losing data
**Independent Test**: Generate events into file with existing content and verify all original entries remain unchanged

- [x] T027 [P] [US3] Implement org-mode file reading in src/ord_plan/parsers/org_mode.py
- [x] T028 [US3] Implement content preservation logic in src/ord_plan/services/file_service.py
- [x] T029 [US3] Add --file parameter handling with stdout fallback in src/ord_plan/cli/generate.py
- [x] T030 [US3] Create new file creation logic in src/ord_plan/services/file_service.py
- [x] T031 [US3] Add file preservation tests in tests/unit/test_file_service.py
- [x] T032 [P] [US3] Add integration test for file preservation in tests/integration/test_file_preservation.py

## Phase 6: User Story 4 - Error Handling and Validation (Priority: P2)

**Goal**: Clear error messages and validation so users can understand and fix configuration issues quickly
**Independent Test**: Provide invalid inputs and verify appropriate error handling

- [x] T033 [P] [US4] Implement cron validation with clear error messages in src/ord_plan/utils/validators.py
- [x] T034 [US4] Add YAML schema validation in src/ord_plan/parsers/yaml_parser.py
- [x] T035 [US4] Implement file validation (permissions, existence) in src/ord_plan/utils/validators.py
- [x] T036 [US4] Add comprehensive error handling in src/ord_plan/cli/generate.py
- [x] T037 [US4] Create error handling tests in tests/unit/test_validators.py
- [x] T038 [P] [US4] Add integration test for error handling in tests/integration/test_error_handling.py

## Phase 7: User Story 5 - Date Protection and Warnings (Priority: P2)

**Goal**: Warnings when generating events for past dates or far future dates so users can confirm intentional actions
**Independent Test**: Attempt to generate events for past dates and far future dates with and without force flag

- [x] T039 [P] [US5] Implement past date detection and warning logic in src/ord_plan/services/date_service.py
- [x] T040 [US5] Implement future date validation (>1 year) in src/ord_plan/services/date_service.py
- [x] T041 [US5] Add --force flag handling in src/ord_plan/cli/generate.py
- [x] T042 [US5] Implement user confirmation prompts in src/ord_plan/cli/generate.py
- [x] T043 [US5] Create date protection tests in tests/unit/test_date_protection.py
- [x] T044 [P] [US5] Add integration test for date protection in tests/integration/test_date_protection.py

## Phase 8: Polish & Cross-Cutting Concerns

- [x] T045 Add comprehensive CLI help and documentation in src/ord_plan/cli/generate.py
- [x] T046 [P] Implement performance optimization for large event sets in src/ord_plan/services/event_service.py
- [x] T047 Add configuration for custom date formats in src/ord_plan/cli/config.py
- [x] T048 Create CLI contract tests in tests/contract/test_generate_command.py
- [x] T049 [P] Add end-to-end performance tests in tests/integration/test_performance.py
- [x] T050 Update documentation with usage examples in docs/usage.md
- [x] T051 [P] Ensure 100% test coverage across all modules

## Dependencies

### User Story Completion Order

```
Phase 3 (US1) → Phase 4 (US2) → Phase 5 (US3) → Phase 6 (US4) → Phase 7 (US5) → Phase 8
```

### Critical Dependencies

- **Phase 1-2**: Must complete before any user story implementation
- **US1 Basic Generation**: Foundation for all other user stories
- **US3 File Preservation**: Required before US4, US5 (they modify file operations)
- **US4 Error Handling**: Enhances all other stories with better validation
- **US2 Date Flexibility**: Can be implemented after basic generation works

## Parallel Execution Opportunities

### Within User Stories

- **US1 Phase**: T011-T017 can be parallel (different model files)
- **US2 Phase**: T025-T026 can be parallel (tests vs implementation)
- **US3 Phase**: T031-T032 can be parallel (tests vs implementation)
- **US4 Phase**: T037-T038 can be parallel (tests vs implementation)
- **US5 Phase**: T043-T044 can be parallel (tests vs implementation)
- **Phase 8**: T045-T051 have various parallel opportunities

### Across Stories

- **Testing**: Many test tasks (T020, T026, T032, T038, T044) can be parallel once implementations are ready
- **Documentation**: T050 can be done in parallel with final testing

## Implementation Strategy

### MVP Scope (User Story 1)

Focus on getting basic event generation working:

1. Complete Phase 1-2 setup
2. Implement US1 with core event generation
3. Add basic tests (T020)
4. Verify org-mode output format
5. Test with provided examples from spec

### Incremental Delivery

1. **First Increment**: US1 - Basic event generation with hardcoded date ranges
2. **Second Increment**: US3 - Add file preservation and output options
3. **Third Increment**: US2 - Add date range flexibility
4. **Fourth Increment**: US4 - Add comprehensive error handling
5. **Final Increment**: US5 - Add date protection and polish

### Testing Strategy

- **Unit Tests**: Each component tested independently (validators, services, models)
- **Integration Tests**: End-to-end workflow testing for each user story
- **Contract Tests**: CLI interface compliance and parameter validation
- **Performance Tests**: Verify <30 second target for 1000 events
- **Coverage**: Target 100% as required by constitution

## Task Statistics

- **Total Tasks**: 51
- **Setup Tasks**: 5
- **Foundational Tasks**: 5
- **User Story 1 Tasks**: 10
- **User Story 2 Tasks**: 6
- **User Story 3 Tasks**: 6
- **User Story 4 Tasks**: 6
- **User Story 5 Tasks**: 6
- **Polish Tasks**: 7

**Parallel Opportunities**: 15 tasks marked as parallelizable across different stories and phases
