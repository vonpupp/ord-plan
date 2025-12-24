# Data Model: Migrate from Poetry to UV

**Feature**: 005-migrate-poetry-to-uv | **Date**: 2025-12-23

## Overview

This is a migration feature that replaces Poetry with UV for dependency management. No new data entities are introduced. The migration affects only tooling configuration and command invocations.

## Entities

No new entities are created in this migration. The existing entities (events, org-mode templates, etc.) remain unchanged.

## Configuration Files Modified

### pyproject.toml

**Purpose**: Project configuration and dependency specification

**Changes**:
- Remove `[tool.poetry]` sections if present (already migrated to PEP 621 format)
- Remove `nox-poetry` from dev dependencies
- Add `tomli-w` to dev dependencies for version manipulation in release workflow

**Structure** (target state):
```toml
[project]
name = "ord-plan"
version = "0.0.1"
description = "..."
dependencies = [
    "click>=8.0.1",
    "pyyaml",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "coverage",
    "mypy",
    "black",
    "isort",
    "flake8",
    "darglint",
    "nox>=2025.11.12,<2026",
    "tomli-w>=1.0.0",  # NEW: Required for version manipulation
]
```

### uv.lock

**Purpose**: Lock file containing resolved dependency versions

**Status**: Already exists (migrated from poetry.lock)

**Changes**: None; file is already in correct format

## Command Mappings

### Poetry to UV Command Equivalents

| Poetry Command | UV Equivalent | Files Affected |
| -------------- | ------------ | -------------- |
| `poetry run <cmd>` | `uv run <cmd>` | tasks.py, .pre-commit-config.yaml |
| `poetry install` | `uv pip install -e .` | README.md, CONTRIBUTING.md |
| `poetry install --with dev` | `uv pip install -e ".[dev]"` | README.md, CONTRIBUTING.md |
| `poetry build` | `uv build` | .github/workflows/release.yml |
| `poetry version` | Custom Python script | .github/workflows/release.yml |

## Migration Stages

### Stage 1: GitHub Workflows

**Files Modified**:
- `.github/workflows/tests.yml`
- `.github/workflows/release.yml`

**Changes**:
- Replace Poetry installation with UV installation
- Remove nox-poetry injection
- Update version detection to use Python + tomli
- Replace `poetry build` with `uv build`

### Stage 2: Noxfile

**Files Modified**:
- `noxfile.py`
- `pyproject.toml`

**Changes**:
- Remove nox-poetry imports
- Replace `session.poetry.export_requirements()` with `uv pip freeze`
- Update session.install() calls (optionally use `uv pip install`)

### Stage 3: Source Code

**Files Checked**:
- All files in `src/ord_plan/`

**Expected Changes**: None (no Poetry commands in source code)

**Verification**: Search for "poetry" references and confirm none found

### Stage 4: Tasks.py

**Files Modified**:
- `tasks.py`

**Changes**:
- Replace all `poetry run` with `uv run` in invoke task commands

### Stage 5: Documentation

**Files Modified**:
- `README.md`
- `CONTRIBUTING.md`
- `AGENTS.md`
- `.pre-commit-config.yaml`
- `Dockerfile`
- `docs/` (any Poetry references)

**Changes**:
- Update installation instructions to use UV
- Remove Poetry installation sections
- Replace `poetry run` with `uv run`
- Update technology lists

## State Transitions

### Before Migration

```
State A: Poetry-based Development
├── Dependencies managed by Poetry
├── Commands: poetry run <cmd>
├── CI/CD: Poetry installed in GitHub Actions
├── Nox: nox-poetry plugin used
└── Docs: Poetry installation instructions
```

### After Migration

```
State B: UV-based Development
├── Dependencies managed by UV
├── Commands: uv run <cmd>
├── CI/CD: UV installed in GitHub Actions
├── Nox: Native nox with UV commands
└── Docs: UV installation instructions
```

### Transition Path

```
State A → Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5 → State B
   (GitHub      (Noxfile)  (Source)   (Tasks)   (Docs)
    Workflows)
```

Each stage must pass all tests before proceeding to the next stage.

## Validation Rules

### Per-Stage Validation

1. **Stage 1**: GitHub Actions workflows must pass on all platforms
2. **Stage 2**: All nox sessions must run successfully
3. **Stage 3**: No Poetry references found in source code
4. **Stage 4**: All invoke tasks must execute correctly
5. **Stage 5**: Documentation accurate; pre-commit hooks pass

### Final Validation

After all stages complete:
- All tests pass (`invoke pytest`, `nox`)
- All linting passes (`invoke lint`)
- Pre-commit hooks pass (`invoke pre-commit`)
- No Poetry commands in any files
- Documentation references UV only

## Data Integrity

### No Data Migration Required

This migration does not involve:
- Database migrations
- File format changes
- Data structure modifications
- API changes

The migration is purely about:
- Tooling replacement (Poetry → UV)
- Command invocation updates
- Documentation updates

### Version Compatibility

The migration maintains backward compatibility with:
- Existing project structure
- Source code functionality
- Test suite behavior
- CLI interface

The only breaking change is: Poetry is no longer required for development.

## Rollback Data

Each migration stage is reversible via git:
- Stage 1: Restore `.github/workflows/*.yml`
- Stage 2: Restore `noxfile.py`, `pyproject.toml`
- Stage 3: N/A (no changes expected)
- Stage 4: Restore `tasks.py`
- Stage 5: Restore documentation files
