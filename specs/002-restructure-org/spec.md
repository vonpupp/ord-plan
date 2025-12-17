# Feature Specification: Repository Restructure

**Feature Branch**: `002-restructure-org`  
**Created**: 2025-12-17  
**Status**: Draft  
**Input**: User description: "I noticed a mistake in the organization, here is the current organization:
❯ tree -d
.
├── ord-plan
│   ├── docs
│   ├── __pycache__
│   ├── src
│   │   └── ord_plan
│   │       ├── cli
│   │       │   └── __pycache__
│   │       ├── models
│   │       │   └── __pycache__
│   │       ├── parsers
│   │       │   └── __pycache__
│   │       ├── __pycache__
│   │       ├── services
│   │       │   └── __pycache__
│   │       └── utils
│   │           └── __pycache__
│   └── tests
│       ├── contract
│   │   └── __pycache__
│       ├── fixtures
│       ├── integration
│   │   └── __pycache__
│       ├── __pycache__
│       └── unit
│           └── __pycache__
└── specs
    └── 001-generate-org
        ├── checklists
        └── contracts

❯ pwd
/home/av/repos/ord-plan
❯ ls -alhtr
total 44K
drwxr-xr-x 33 av av 4.0K Dec 16 20:52 ../
drwxr-xr-x  5 av av 4.0K Dec 16 20:56 .specify/
drwxr-xr-x  3 av av 4.0K Dec 17 23:40 specs/
drwxr-xr-x  3 av av 4.0K Dec 17 07:05 .ruff_cache/
-rw-r--r--  1 av av  128 Dec 17 07:51 .gitignore
drwxr-xr-x  4 av av 4.0K Dec 17 13:29 .opencode/
drwxr-xr-x  3 av av 4.0K Dec 17 13:34 .pytest_cache/
drwxr-xr-x  9 av av 4.0K Dec 17 14:45 ord-plan/
drwxr-xr-x  9 av av 4.0K Dec 17 14:46 ./
-rw-------  1 av av 2.0K Dec 17 14:47 AGENTS.md
drwxr-xr-x  7 av av 4.0K Dec 17 15:02 .git/

❯ cd ord-plan/
❯ ls -alhtr
total 136K
-rw-r--r-- 1 av av   19 Dec 16 20:54 .gitattributes
-rw-r--r-- 1 av av  122 Dec 16 20:54 .gitignore
-rw-r--r-- 1 av av  191 Dec 16 20:54 .readthedocs.yml
-rw-r--r-- 1 av av 5.4K Dec 16 20:54 CODE_OF_CONDUCT.md
-rw-r--r-- 1 av av   29 Dec 16 20:54 .darglint
-rw-r--r-- 1 av av  133 Dec 16 20:54 codecov.yml
-rw-r--r-- 1 av av 6.8K Dec 16 20:54 noxfile.py
-rw-r--r-- 1 av av 1.8K Dec 16 20:54 .pre-commit-config.yaml
-rw-r--r-- 1 av av 2.8K Dec 16 20:54 CONTRIBUTING.md
-rw-r--r-- 1 av av  263 Dec 16 20:54 .flake8
drwxr-xr-x 3 av av 4.0K Dec 16 20:54 src/
-rw-r--r-- 1 av av  36K Dec 16 20:54 LICENSE
drwxr-xr-x 2 av av 4.0K Dec 16 20:54 docs/
drwxr-xr-x 3 av av 4.0K Dec 16 20:54 .github/
-rw-r--r-- 1 av av  518 Dec 16 20:54 .cookiecutter.json
-rw-r--r-- 1 av av  223 Dec 17 07:26 conftest.py
drwxr-xr-x 7 dr av 4.0K Dec 17 13:12 tests/
-rw-r--r-- 1 av av  11K Dec 17 14:12 README.md
drwxr-xr-x 5 av av 4.0K Dec 17 14:14 .venv/
-rw-r--r-- 1 av av 2.0K Dec 17 14:24 pyproject.toml
drwxr-xr-x 9 av av 4.0K Dec 17 14:46 ../
drwxr-xr-x 7 av av 4.0K Dec 17 15:12 ./

However, I want the ord-plan, the python package, meaning, where README, LICENSE etc are, to be at the top of the hierarchy. In other words, I want ord-plan/ord-plan to be emptied, so I can manually delete it myself after review.

I want you to make the changes required for that refactoring. This is NOT a new feature - it is a one-time repository refactoring operation. I want you to consider code, tests, constitution, specs documents, plan documents, everything! I want you to be thorough and double check references, links, everything and that everything works after the refactoring by running the tests. The approach should use refactoring scripts, not new CLI commands, since this is a one-time infrastructure operation. "

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Move Repository Root Files (Priority: P1)

As a developer, I want all the Python package files (README, LICENSE, pyproject.toml, etc.) to be at the repository root level so that the repository follows standard Python project conventions and the ord-plan subdirectory can be removed.

**Why this priority**: This is the core requirement that enables the repository restructuring. Without moving these files, the current nested structure cannot be resolved.

**Independent Test**: Can be fully tested by moving all root-level files from ord-plan/ to the repository root and verifying that the package structure is valid and tests run successfully.

**Acceptance Scenarios**:

1. **Given** files are in ord-plan/ subdirectory, **When** restructuring is applied, **Then** all package files (README.md, LICENSE, pyproject.toml, src/, tests/, docs/, .github/) are moved to repository root
2. **Given** tests run successfully in current structure, **When** files are moved, **Then** all tests continue to pass without modification

---

### User Story 2 - Update All Internal References (Priority: P1)

As a developer, I want all internal file references, paths, and links to be updated so that the repository functions correctly after restructuring.

**Why this priority**: Without updating references, the moved files will have broken links and the repository will be non-functional.

**Independent Test**: Can be fully tested by searching for all references to ord-plan/ paths and updating them to work with the new structure, then verifying all functionality works.

**Acceptance Scenarios**:

1. **Given** documentation contains relative paths to ord-plan/, **When** restructuring is applied, **Then** all paths are updated to remove ord-plan/ prefix
2. **Given** configuration files reference ord-plan/ directories, **When** restructuring is applied, **Then** all references point to the correct new locations
3. **Given** CI/CD workflows reference ord-plan/ paths, **When** restructuring is applied, **Then** all workflow paths are updated

---

### User Story 3 - Preserve All Development Workflow (Priority: P1)

As a developer, I want all development commands, tests, and workflows to function identically after restructuring so that the development experience remains unchanged.

**Why this priority**: The restructuring should be transparent to developers and not disrupt any existing workflows or automation.

**Independent Test**: Can be fully tested by running the complete test suite, linting, and build processes before and after restructuring to ensure identical results.

**Acceptance Scenarios**:

1. **Given** all tests pass before restructuring, **When** restructuring is applied, **Then** all tests continue to pass with identical results
2. **Given** linting and formatting tools work before restructuring, **When** restructuring is applied, **Then** all code quality tools continue to function
3. **Given** CI/CD pipelines work before restructuring, **When** restructuring is applied, **Then** all pipelines continue to function correctly

---

### Edge Cases

The following edge cases MUST be addressed during refactoring:

- **Absolute paths**: Configuration files with absolute paths must be identified and manually reviewed
- **Relative imports**: Python relative imports must be validated after src/ directory movement  
- **Git history**: All git history must be preserved using git mv operations
- **External links**: External links to repository are out of scope, but internal cross-references must be updated

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: All package configuration files (pyproject.toml, setup.cfg, etc.) MUST be moved to repository root
- **FR-002**: Source code directory (src/) MUST be moved to repository root while preserving internal structure
- **FR-003**: Test directory (tests/) MUST be moved to repository root while preserving all test files and fixtures
- **FR-004**: Documentation directory (docs/) MUST be moved to repository root
- **FR-005**: CI/CD configuration (.github/) MUST be moved to repository root
- **FR-006**: All project metadata files (README.md, LICENSE, CONTRIBUTING.md, etc.) MUST be moved to repository root
- **FR-007**: All internal file references and paths MUST be updated to reflect new structure
- **FR-008**: All relative imports in Python code MUST continue to function after restructuring
- **FR-009**: All test fixtures and paths in test files MUST be updated to work with new structure
- **FR-010**: Documentation links and cross-references MUST be updated to reflect new file locations
- **FR-011**: All development commands (lint, test, build) MUST work identically after restructuring
- **FR-012**: All existing functionality MUST be preserved - no feature changes allowed
- **FR-013**: Edge cases MUST be handled: absolute paths in config files, relative import resolution, git history preservation, external link handling

### Key Entities *(include if feature involves data)*

- **Repository Root**: The top-level directory containing the Python project files
- **Package Configuration**: pyproject.toml, setup.cfg, and other build configuration files
- **Source Code**: The src/ directory containing all Python modules and packages
- **Test Suite**: The tests/ directory with unit tests, integration tests, and fixtures
- **Documentation**: The docs/ directory with project documentation
- **CI/CD Configuration**: GitHub Actions workflows and related automation files

## Clarifications

### Session 2025-12-17

- Q: How should external integration dependencies that reference the current ord-plan/ structure be handled? → A: Only handle internal references; ignore external dependencies
- Q: What is the preferred approach for preserving git history when moving files? → A: Create a single commit showing all moves
- Q: Should temporary directories be used during file movement process? → A: Direct move to final locations to avoid confusion

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of files successfully moved from ord-plan/ to repository root without data loss
- **SC-002**: All 100% of internal references and paths updated to work with new structure
- **SC-003**: 100% test pass rate achieved after restructuring (identical to before restructuring)
- **SC-004**: All development commands (test, lint, build) complete successfully with identical results
- **SC-005**: Zero broken links or references in documentation after restructuring
- **SC-006**: Repository follows standard Python project structure conventions after restructuring