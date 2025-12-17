---

description: "Task list for repository restructuring implementation"
---

# Tasks: Repository Restructure

**Input**: Design documents from `/specs/002-restructure-org/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **CLI Tool**: `src/ord_plan/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume CLI tool structure - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create repository restructuring project structure per implementation plan
- [ ] T002 Initialize Python project with Poetry dependencies (Click, pytest, sed, git tools)
- [ ] T003 [P] Configure restructuring validation tools (pytest, ruff, git status checks)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Setup git repository state validation for clean working directory
- [ ] T005 [P] Create file movement utilities for git mv operations with history preservation
- [ ] T006 [P] Create path mapping system for reference updates using regex patterns
- [ ] T007 Setup validation framework for repository state transitions
- [ ] T008 Create import statement parsing and update utilities for Python code

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Move Repository Root Files (Priority: P1) 🎯 MVP

**Goal**: Move all Python package files (README, LICENSE, pyproject.toml, etc.) to repository root level

**Independent Test**: Can be fully tested by moving all root-level files from ord-plan/ to the repository root and verifying that the package structure is valid and tests run successfully.

### Implementation for User Story 1

- [x] T009 [US1] Create directory movement script in scripts/restructure/move_directories.py
- [x] T010 [P] [US1] Move src/ directory from ord-plan/ to repository root using git mv in scripts/restructure/move_directories.py
- [x] T011 [P] [US1] Move tests/ directory from ord-plan/ to repository root using git mv in scripts/restructure/move_directories.py
- [x] T012 [P] [US1] Move docs/ directory from ord-plan/ to repository root using git mv in scripts/restructure/move_directories.py
- [x] T013 [P] [US1] Move .github/ directory from ord-plan/ to repository root using git mv in scripts/restructure/move_directories.py
- [x] T014 [P] [US1] Move project metadata files (README.md, LICENSE, pyproject.toml, etc.) from ord-plan/ to repository root in scripts/restructure/move_files.py
- [x] T015 [US1] Create validation script to verify all files moved successfully in scripts/restructure/validate_moves.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Update All Internal References (Priority: P1)

**Goal**: Update all internal file references, paths, and links to work with new repository structure

**Independent Test**: Can be fully tested by searching for all references to ord-plan/ paths and updating them to work with the new structure, then verifying all functionality works.

### Implementation for User Story 2

- [x] T016 [P] [US2] Update Python import statements to remove ord_plan prefix in scripts/restructure/update_imports.py
- [x] T017 [P] [US2] Update pyproject.toml path references to remove ord-plan/ prefixes in scripts/restructure/update_config.py
- [x] T018 [P] [US2] Update test file imports and fixture paths in scripts/restructure/update_tests.py
- [x] T019 [P] [US2] Update documentation cross-references in scripts/restructure/update_docs.py
- [x] T020 [P] [US2] Update CI/CD workflow paths in scripts/restructure/update_workflows.py
- [x] T021 [US2] Create comprehensive reference update validation in scripts/restructure/validate_references.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Preserve All Development Workflow (Priority: P1)

**Goal**: Ensure all development commands, tests, and workflows function identically after restructuring

**Independent Test**: Can be fully tested by running the complete test suite, linting, and build processes before and after restructuring to ensure identical results.

### Implementation for User Story 3

- [ ] T022 [US3] Create workflow validation script to test all development commands in scripts/restructure/validate_workflows.py
- [ ] T023 [P] [US3] Validate pytest runs successfully after restructuring in scripts/restructure/validate_workflows.py
- [ ] T024 [P] [US3] Validate ruff linting works after restructuring in scripts/restructure/validate_workflows.py
- [ ] T025 [P] [US3] Validate package discovery and installation in scripts/restructure/validate_workflows.py
- [ ] T026 [US3] Create before/after comparison tests to ensure identical functionality in scripts/restructure/compare_results.py
- [ ] T027 [US3] Create final comprehensive validation report in scripts/restructure/final_validation.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T028 [P] Create CLI command interface for restructuring operations in src/ord_plan/cli/restructure.py
- [ ] T029 [P] Add comprehensive error handling and rollback capabilities in scripts/restructure/error_handling.py
- [ ] T030 [P] Add dry-run mode to preview all changes before execution in scripts/restructure/dry_run.py
- [ ] T031 Create documentation updates for new repository structure in docs/usage.md
- [ ] T032 Update AGENTS.md to reflect new project structure
- [ ] T033 Run comprehensive validation and create restructuring completion report

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (US1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (US2)**: Can start after Foundational (Phase 2) - Depends on US1 completion (files must exist before references can be updated)
- **User Story 3 (US3)**: Can start after Foundational (Phase 2) - Depends on US1 and US2 completion (all files and references must be updated before workflows can be validated)

### Within Each User Story

- File movement tasks can run in parallel within US1
- Reference update tasks can run in parallel within US2  
- Validation tasks can run in parallel within US3
- Each story should be completed before moving to the next story

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- File movement tasks in US1 marked [P] can run in parallel (different directories)
- Reference update tasks in US2 marked [P] can run in parallel (different file types)
- Validation tasks in US3 marked [P] can run in parallel (different tools)
- Polish phase tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1 & 2

```bash
# Launch all file movements for User Story 1 together:
Task: "Move src/ directory from ord-plan/ to repository root using git mv in scripts/restructure/move_directories.py"
Task: "Move tests/ directory from ord-plan/ to repository root using git mv in scripts/restructure/move_directories.py"
Task: "Move docs/ directory from ord-plan/ to repository root using git mv in scripts/restructure/move_directories.py"

# Launch all reference updates for User Story 2 together:
Task: "Update Python import statements to remove ord_plan prefix in scripts/restructure/update_imports.py"
Task: "Update pyproject.toml path references to remove ord-plan/ prefixes in scripts/restructure/update_config.py"
Task: "Update test file imports and fixture paths in scripts/restructure/update_tests.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test file moves independently
5. Review and approve before proceeding with reference updates

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Review file structure
3. Add User Story 2 → Test independently → Validate reference updates
4. Add User Story 3 → Test independently → Validate all workflows
5. Complete Polish phase → Full restructuring completion

### Sequential Strategy (Recommended)

Due to dependencies between stories:

1. Team completes Setup + Foundational together
2. Complete User Story 1 (file movements) → Validate
3. Complete User Story 2 (reference updates) → Validate  
4. Complete User Story 3 (workflow validation) → Validate
5. Complete Polish phase for CLI interface and documentation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Use git mv for all file movements to preserve history
- Validate after each phase before proceeding
- Avoid: manual copy/delete operations, losing git history, breaking existing workflows
- All operations must be atomic within each phase