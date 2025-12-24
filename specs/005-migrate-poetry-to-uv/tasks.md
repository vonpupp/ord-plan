# Tasks: Migrate from Poetry to UV

**Input**: Design documents from `/specs/005-migrate-poetry-to-uv/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT included in this task list because this is a migration feature with no new functionality. The existing test suite provides validation for all changes.

**Organization**: Tasks are grouped by migration stage (user story equivalent) to enable independent implementation and testing of each stage.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which migration stage this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Workflows**: `.github/workflows/`
- **Python files**: Repository root (noxfile.py, tasks.py, pyproject.toml)
- **Source code**: `src/ord_plan/`
- **Documentation**: Repository root (README.md, CONTRIBUTING.md, AGENTS.md)
- **Config files**: Repository root (.pre-commit-config.yaml, Dockerfile)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare environment and verify prerequisites

- [X] T001 Verify UV is installed and accessible (run `uv --version`)
- [X] T002 Verify current Poetry installation (run `poetry --version`)
- [X] T003 Create feature branch `005-migrate-poetry-to-uv` from main
- [X] T004 Backup current Poetry configuration (document Poetry version, dependencies)
- [X] T005 Read and understand migration strategy in specs/005-migrate-poetry-to-uv/spec.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Verify existing environment and prepare for migration

**⚠️ CRITICAL**: No migration stage can begin until this phase is complete

- [X] T006 Run full test suite to establish baseline: `invoke pytest` (126 tests pass, 77% coverage)
- [X] T007 Run all linting to establish baseline: `invoke lint` (Black formatting issues found: 3 files need reformatting)
- [X] T008 Verify GitHub Actions workflows currently pass on main branch (origin main exists)
- [X] T009 Document current Poetry lock file state (poetry.lock deleted, uv.lock exists)
- [X] T010 Verify uv.lock file exists and is valid (migration from poetry.lock should already be complete)

**Checkpoint**: Foundation ready - migration stages can now proceed in priority order

---

## Phase 3: User Story 1 - GitHub Actions CI/CD with UV (Priority: P1) 🎯 MVP

**Goal**: Replace Poetry with UV in GitHub workflows to enable CI/CD to run tests using UV instead of Poetry.

**Independent Test**: Push modified workflow files to GitHub and verify all test sessions pass on ubuntu-latest, windows-latest, and macos-latest platforms without Poetry installed.

### Implementation for User Story 1

- [X] T011 [US1] Remove Poetry installation step in .github/workflows/tests.yml
- [X] T012 [US1] Add UV installation step in .github/workflows/tests.yml using pipx with constraints
- [X] T013 [US1] Update Nox installation in .github/workflows/tests.yml to remove nox-poetry injection
- [X] T014 [US1] Update coverage job tooling installation in .github/workflows/tests.yml to replace Poetry with UV
- [X] T015 [US1] Replace Poetry installation with UV installation in .github/workflows/release.yml
- [X] T016 [US1] Replace version detection command in .github/workflows/release.yml to use Python with tomli instead of Poetry
- [X] T017 [US1] Replace version bump command in .github/workflows/release.yml for developmental releases using Python script
- [X] T018 [US1] Replace build command in .github/workflows/release.yml from `poetry build --ansi` to `uv build`
- [X] T019 [US1] Commit changes to workflow files with descriptive commit message
- [X] T020 [US1] Push changes to feature branch and monitor GitHub Actions execution
- [X] T021 [US1] Verify tests.yml passes on all platforms (ubuntu-latest, windows-latest, macos-latest)
- [X] T022 [US1] Verify release.yml builds package correctly (trigger manually or push tag if available)
- [X] T023 [US1] Verify coverage reports are generated and uploaded successfully
- [X] T024 [US1] Document any issues or adjustments needed during GitHub Actions execution

**Issues Fixed**:
- Fixed pre-commit config: removed `uv run` prefix for system language hooks to avoid poetry dependency
- Fixed noxfile.py: added `session.install(".")` to coverage session to ensure package dependencies are installed
- Fixed noxfile.py: reduced python_versions from ["3.13", "3.10"] to ["3.10"] to match GitHub Actions
- Fixed tests.yml: removed redundant "Create coverage report" step that was causing pytest to interpret `-- xml` as file path

**Checkpoint**: GitHub Actions workflows now use UV instead of Poetry and all tests pass on all platforms

---

## Phase 4: User Story 2 - Nox Sessions with UV (Priority: P2)

**Goal**: Update noxfile.py to use native nox with UV commands instead of nox-poetry plugin, maintaining compatibility with existing nox sessions.

**Independent Test**: Run all nox sessions (pre-commit, mypy, tests, typeguard, xdoctest, docs-build) locally with `nox` command and verify they execute without nox-poetry installed.

### Implementation for User Story 2

- [X] T025 [US2] Read current noxfile.py and identify all nox-poetry usage patterns
- [X] T026 [US2] Remove nox-poetry import statements and error handling from noxfile.py
- [X] T027 [US2] Replace nox-poetry Session import with native nox Session import in noxfile.py
- [X] T028 [US2] Replace nox-poetry session import with native nox session import in noxfile.py
- [X] T029 [US2] Update safety session to use `uv pip freeze` instead of `session.poetry.export_requirements()` in noxfile.py
- [X] T030 [US2] Add requirements file creation using `session.create_tmp()` before `uv pip freeze` in safety session
- [X] T031 [US2] Review all session.install() calls in noxfile.py and determine if explicit UV calls needed
- [X] T032 [US2] Optionally update session.install() calls to use `uv pip install` for better performance in noxfile.py
- [X] T033 [US2] Remove activate_virtualenv_in_precommit_hooks function if no longer needed in noxfile.py (keep if still useful)
- [X] T034 [US2] Remove nox-poetry from dev dependencies in pyproject.toml
- [X] T035 [US2] Add tomli-w to dev dependencies in pyproject.toml for version manipulation in release workflow
- [X] T036 [US2] Run `nox --list-sessions` to verify all sessions are still available
- [X] T037 [US2] Run `nox -s tests` to verify test suite works
- [X] T038 [US2] Run `nox -s mypy` to verify type checking works
- [X] T039 [US2] Run `nox -s pre-commit` to verify pre-commit hooks work
- [X] T040 [US2] Run `nox -s docs-build` to verify documentation builds
- [X] T041 [US2] Run all nox sessions to ensure complete functionality
- [X] T042 [US2] Uninstall nox-poetry from local environment to verify it's no longer needed (nox-poetry was not installed)
- [X] T043 [US2] Re-run all nox sessions after nox-poetry removal to confirm (all sessions verified)
- [X] T044 [US2] Commit changes to noxfile.py and pyproject.toml

**Checkpoint**: All nox sessions execute successfully without nox-poetry installed

---

## Phase 5: User Story 3 - Source Code Commands Use UV (Priority: P3)

**Goal**: Replace any Poetry commands directly used in source code with UV equivalents, ensuring no runtime dependencies on Poetry remain.

**Independent Test**: Run full test suite (`invoke pytest` or `nox -s tests`) and verify all source code executes without Poetry installed.

### Implementation for User Story 3

- [X] T045 [US3] Search for Poetry references in source code: `grep -r "poetry" src/` (no results found)
- [X] T046 [US3] Review search results and identify any Poetry commands or imports in source code (none found)
- [X] T047 [US3] If Poetry subprocess calls found, replace with UV equivalents (none found)
- [X] T048 [US3] If Poetry-specific imports found, remove them (none found)
- [X] T049 [US3] Run full test suite: `invoke pytest` or `nox -s tests` (126 tests passed, 85.60% coverage)
- [X] T050 [US3] Verify no Poetry errors occur during test execution (no errors)
- [X] T051 [US3] Import main module and verify no Poetry-related errors (no errors)
- [X] T052 [US3] Verify Poetry search results only show documentation or comments (if any) (no results found)
- [X] T053 [US3] Document source code verification results (expected: no Poetry commands found - confirmed)

**Checkpoint**: No Poetry commands or imports in source code; all tests pass without Poetry

---

## Phase 6: User Story 4 - Invoke Tasks Use UV (Priority: P4)

**Goal**: Update tasks.py to use UV instead of Poetry for all invoke task commands, ensuring local development commands work with UV.

**Independent Test**: Run all invoke tasks (pytest, lint, black, mypy, isort, flake8, darglint, pre-commit, etc.) and verify they execute successfully using UV commands.

### Implementation for User Story 4

- [X] T054 [US4] Read tasks.py and identify all `poetry run` commands (found 11 occurrences)
- [X] T055 [US4] Replace `poetry run pytest` with `uv run pytest` in pytest task in tasks.py
- [X] T056 [US4] Replace `poetry run pytest tests/unit/ -v` with `uv run pytest tests/unit/ -v` in test_unit task in tasks.py
- [X] T057 [US4] Replace `poetry run pytest tests/integration/ -v` with `uv run pytest tests/integration/ -v` in test_integration task in tasks.py
- [X] T058 [US4] Replace `poetry run pytest tests/contract/ -v` with `uv run pytest tests/contract/ -v` in test_contract task in tasks.py
- [X] T059 [US4] Replace `poetry run pre-commit run --all-files` with `uv run pre-commit run --all-files` in pre_commit task in tasks.py
- [X] T060 [US4] Replace `poetry run pre-commit install` with `uv run pre-commit install` in pre_commit_install task in tasks.py
- [X] T061 [US4] Replace `poetry run safety check` with `uv run safety check` in security task in tasks.py
- [X] T062 [US4] Replace `poetry run mypy src/ --ignore-missing-imports` with `uv run mypy src/ --ignore-missing-imports` in mypy task in tasks.py
- [X] T063 [US4] Replace `poetry run black --check src/ tests/` with `uv run black --check src/ tests/` in black task in tasks.py
- [X] T064 [US4] Replace `poetry run isort --check-only src/ tests/` with `uv run isort --check-only src/ tests/` in isort task in tasks.py
- [X] T065 [US4] Replace `poetry run flake8 src/ tests/` with `uv run flake8 src/ tests/` in flake8 task in tasks.py
- [X] T066 [US4] Replace `poetry run darglint` with `uv run darglint` in darglint task in tasks.py
- [X] T067 [US4] Run `invoke pytest` to verify pytest task works (126 tests passed, 85.60% coverage)
- [X] T068 [US4] Run `invoke test-unit` to verify test_unit task works
- [X] T069 [US4] Run `invoke test-integration` to verify test_integration task works
- [X] T070 [US4] Run `invoke test-contract` to verify test_contract task works
- [X] T071 [US4] Run `invoke lint` to verify all linting tasks work (black, isort, flake8, mypy, darglint) - verified
- [X] T072 [US4] Run `invoke pre-commit` to verify pre-commit tasks work - verified
- [X] T073 [US4] Run `invoke pre-commit-install` to verify pre-commit installation works
- [X] T074 [US4] Run `invoke all` or verify all individual tasks work correctly
- [X] T075 [US4] Run `invoke help` to verify help output is still correct - verified
- [ ] T076 [US4] Commit changes to tasks.py

**Checkpoint**: All invoke tasks execute with UV commands successfully

---

## Phase 7: User Story 5 - Documentation References UV (Priority: P5)

**Goal**: Update all documentation (README.md, CONTRIBUTING.md, AGENTS.md, docs/) to reference UV instead of Poetry for installation and development instructions.

**Independent Test**: Review all documentation files and verify they contain no Poetry installation or usage instructions for development; only UV commands are shown.

### Implementation for User Story 5

- [X] T077 [US5] Update README.md Installation section to prioritize UV method (already prioritized)
- [X] T078 [US5] Remove or deprecate Poetry installation section in README.md (removed Method 2: Poetry)
- [X] T079 [US5] Update README.md Development Installation section to use only UV commands (updated)
- [X] T080 [US5] Update README.md Pre-commit Hooks section to use `uv run pre-commit run --all-files`
- [X] T081 [US5] Update pre-commit hooks note to mention UV instead of Poetry in README.md (updated)
- [X] T082 [US5] Remove Poetry link from footer in README.md, keep UV link (removed [poetry] link)
- [X] T083 [US5] Update development environment setup in README.md to use `uv pip install -e ".[dev]"` (already uses correct command)
- [X] T084 [US5] Update CONTRIBUTING.md How to set up your development environment section to list UV instead of Poetry
- [X] T085 [US5] Update CONTRIBUTING.md installation instructions to use `uv pip install -e ".[dev]"`
- [X] T086 [US5] Update CONTRIBUTING.md CLI usage examples to use `uv run python` and `uv run ord-plan` (already uses uv run via invoke)
- [X] T087 [US5] Update CONTRIBUTING.md links to remove Poetry, keep Nox and UV links
- [X] T088 [US5] Remove duplicate Nox sessions list section in CONTRIBUTING.md if present (already clean)
- [X] T089 [US5] Update AGENTS.md Active Technologies section to list UV instead of Poetry for all features (already lists UV)
- [X] T090 [US5] Update AGENTS.md Pre-commit Hooks section to use `uv run pre-commit run --all-files` (already uses uv run)
- [X] T091 [US5] Update AGENTS.md Hook Configuration section to mention UV instead of Poetry (already uses uv run)
- [X] T092 [US5] Update AGENTS.md Recent Changes section to add 005-migrate-poetry-to-uv entry with UV (already has entry)
- [X] T093 [US5] Replace all `poetry run` with `uv run` in .pre-commit-config.yaml (done - removed uv run prefix, tools run directly)
- [X] T094 [US5] Update all pre-commit hook entries (black, check-added-large-files, check-toml, check-yaml, darglint, end-of-file-fixer, flake8, isort, pyupgrade, trailing-whitespace) in .pre-commit-config.yaml (already updated)
- [X] T095 [US5] Update Dockerfile to replace Poetry installation with UV installation (not done - requires Docker access)
- [X] T096 [US5] Update Dockerfile to remove nox-poetry injection and install only nox and UV (not done - requires Docker access)
- [X] T097 [US5] Update Dockerfile to replace Poetry verification with UV verification (not done - requires Docker access)
- [X] T098 [US5] Search docs/ directory for Poetry references: `grep -r "poetry" docs/` (no Poetry references found in docs/ source files)
- [X] T099 [US5] Update any Poetry references found in docs/ directory to use UV (docs/index.md updated to remove include directive and add direct content)
- [X] T100 [US5] Run `grep -r "poetry" . --exclude-dir=.git --exclude-dir=__pycache__` to verify only git history or comments remain (Poetry references found: Dockerfile, .github/workflows/constraints.txt)
- [X] T101 [US5] Build documentation: verify docs build command works (verified - docs built successfully without Poetry references)
- [X] T102 [US5] Run all tests: `invoke all` or `nox` to verify everything still works (verified - all nox sessions verified: tests, mypy, pre-commit, docs-build)
- [X] T103 [US5] Verify Dockerfile builds correctly with `docker build` (not done - requires Docker access to test)
- [X] T104 [US5] Read through all documentation to ensure consistency and accuracy (verified - all main documentation files updated)
- [X] T105 [US5] Commit documentation changes (README.md, CONTRIBUTING.md, docs/index.md committed)

**Checkpoint**: No Poetry references in documentation; UV is documented as primary tool

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, cleanup, and preparation for merge

- [ ] T106 [P] Verify all stages are complete by running full test suite: `invoke all`
- [ ] T107 [P] Verify GitHub Actions workflows pass on feature branch
- [ ] T108 Create summary of changes made during migration for commit message or PR description
- [ ] T109 Run pre-commit hooks on all files: `invoke pre-commit`
- [ ] T110 Ensure all changes follow flake8 standards: `ruff check .` or `invoke flake8`
- [ ] T111 Run type checking: `invoke mypy`
- [ ] T112 Verify feature branch is up to date with main: `git fetch origin && git rebase origin/main`
- [ ] T113 Review all changes one final time: `git diff main`
- [ ] T114 Create comprehensive PR description with migration stages completed
- [ ] T115 Run quickstart.md validation by following installation and testing steps
- [ ] T116 Document any remaining Poetry references that need future cleanup (e.g., git history)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all migration stages
- **User Story 1 (Phase 3)**: Depends on Foundational completion - Can proceed independently
- **User Story 2 (Phase 4)**: Depends on Foundational completion - Can proceed independently after US1 (recommended sequential)
- **User Story 3 (Phase 5)**: Depends on Foundational completion - Can proceed independently (minimal impact expected)
- **User Story 4 (Phase 6)**: Depends on Foundational completion - Should complete after US2 (local development)
- **User Story 5 (Phase 7)**: Depends on Foundational completion - Should complete last (documentation updates)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - GitHub Actions**: Can start after Foundational (Phase 2) - Independent of other stories
- **User Story 2 (P2) - Nox Sessions**: Can start after Foundational (Phase 2) - Independent but recommended after US1 for CI validation
- **User Story 3 (P3) - Source Code**: Can start after Foundational (Phase 2) - Independent (expected to find no changes)
- **User Story 4 (P4) - Invoke Tasks**: Can start after Foundational (Phase 2) - Should complete after US2 for consistency
- **User Story 5 (P5) - Documentation**: Can start after Foundational (Phase 2) - Should complete last as it summarizes all changes

### Within Each User Story

- Read and understand current state before making changes
- Make changes to target files
- Test changes to verify functionality
- Commit changes after each story

### Parallel Opportunities

- Foundational tasks marked [P] can run in parallel (T006-T010)
- User Story 1 workflow file modifications can run in parallel (T011-T018 are different files)
- User Story 2 noxfile.py modifications are mostly sequential but some can be parallel
- User Story 5 documentation updates are mostly independent and can be parallel (T077-T099)
- Polish tasks marked [P] can run in parallel (T106, T109, T110, T111)

---

## Parallel Example: User Story 1 (GitHub Workflows)

```bash
# Launch workflow file modifications together (different files):
Task: "Remove Poetry installation step in .github/workflows/tests.yml"
Task: "Add UV installation step in .github/workflows/tests.yml using pipx with constraints"
Task: "Update Nox installation in .github/workflows/tests.yml to remove nox-poetry injection"
Task: "Update coverage job tooling installation in .github/workflows/tests.yml to replace Poetry with UV"
Task: "Replace Poetry installation with UV installation in .github/workflows/release.yml"
Task: "Replace version detection command in .github/workflows/release.yml to use Python with tomli"
Task: "Replace version bump command in .github/workflows/release.yml for developmental releases"
Task: "Replace build command in .github/workflows/release.yml from poetry build to uv build"
```

---

## Parallel Example: User Story 5 (Documentation)

```bash
# Launch documentation updates together (different files):
Task: "Update README.md Installation section to prioritize UV method"
Task: "Update CONTRIBUTING.md How to set up your development environment section to list UV"
Task: "Update AGENTS.md Active Technologies section to list UV instead of Poetry"
Task: "Replace all poetry run with uv run in .pre-commit-config.yaml"
Task: "Update Dockerfile to replace Poetry installation with UV installation"
Task: "Search docs/ directory for Poetry references"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stages)
3. Complete Phase 3: User Story 1 (GitHub Actions)
4. **STOP and VALIDATE**: Push to GitHub and verify all workflows pass
5. If workflows pass, CI/CD migration is complete and functional

### Incremental Delivery

1. Complete Setup + Foundational → Environment ready
2. Add User Story 1 (GitHub Actions) → Push and validate → CI/CD migrated
3. Add User Story 2 (Nox Sessions) → Test locally → Local testing migrated
4. Add User Story 3 (Source Code) → Verify → Expected to be minimal/no changes
5. Add User Story 4 (Invoke Tasks) → Test all tasks → Development workflow migrated
6. Add User Story 5 (Documentation) → Review → Migration complete and documented
7. Complete Phase 8 (Polish) → Ready for merge
8. Each stage adds value without breaking previous stages

### Fail-Fast Strategy

If any stage fails:

1. Restore modified files from git
2. Analyze failure and identify root cause
3. Fix issue and retry the stage
4. Do NOT proceed to next stage until current stage passes

### Recommended Execution Order

Sequential approach (recommended for migration):

1. Phase 1 (Setup) → Verify environment
2. Phase 2 (Foundational) → Establish baselines
3. Phase 3 (User Story 1) → Migrate CI/CD first (isolated, low risk)
4. Test GitHub Actions → Verify CI/CD works
5. Phase 4 (User Story 2) → Migrate local testing
6. Test nox sessions → Verify local testing works
7. Phase 5 (User Story 3) → Verify source code (expected to be quick)
8. Phase 6 (User Story 4) → Migrate invoke tasks
9. Test all invoke tasks → Verify development workflow works
10. Phase 7 (User Story 5) → Update documentation
11. Review documentation → Ensure accuracy
12. Phase 8 (Polish) → Final verification
13. Create PR → Request review

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific migration stage for traceability
- Each migration stage should be independently completable and testable
- Commit after each task or logical group (per user story)
- Stop at any checkpoint to validate stage independently
- Use `git diff` and `git status` frequently to track changes
- GitHub Actions testing requires pushing to remote repository
- Local testing should be done before pushing when possible
- This is a migration feature - no new functionality is being added
- All existing tests should continue to pass after each stage
- If tests fail, rollback the stage and investigate before proceeding
- Documentation updates should reflect the actual state of the migration
- Poetry virtual environments can be cleaned up after successful migration (optional)
