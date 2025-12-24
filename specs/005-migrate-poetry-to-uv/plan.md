# Implementation Plan: Migrate from Poetry to UV

**Branch**: `005-migrate-poetry-to-uv` | **Date**: 2025-12-23 | **Spec**: [spec.md](/specs/005-migrate-poetry-to-uv/spec.md)
**Input**: Feature specification from `/specs/005-migrate-poetry-to-uv/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Migrate the ord-plan codebase from Poetry to UV for dependency management across 5 stages: GitHub workflows, noxfile.py, source code, tasks.py, and documentation. UV provides faster dependency resolution and aligns with hypermodern Python standards. Migration maintains all existing functionality and test coverage.

## Technical Context

**Language/Version**: Python 3.7+ (as specified in pyproject.toml)
**Primary Dependencies**: Click (>=8.0.1), PyYAML, UV for dependency management (migrating from Poetry)
**Storage**: Files (template generation output - org-mode and JSON)
**Testing**: pytest with existing coverage maintained
**Target Platform**: Linux/macOS/Windows (CLI tool)
**Project Type**: Single (CLI tool - determines source structure)
**Performance Goals**: Not applicable (migration only, performance not measured)
**Constraints**: All tests must pass after each migration stage; fail entire migration if any stage fails
**Scale/Scope**: Dependency management migration across CI/CD, local development, source code, and documentation

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

### Required Constitution Compliance Gates

- **✅ CLI-First Design**: Migration preserves all CLI functionality; no changes to command-line interface
- **✅ Test-Driven Development**: All existing tests must pass after each migration stage; no new code added that requires new tests
- **✅ Org-Mode Native**: Primary output format remains org-mode; migration affects only tooling, not output
- **✅ Template Generation Focus**: Core template generation functionality unchanged; only dependency management tools replaced
- **⚠️ Hypermodern Python Standards**: Constitution mentions "Poetry for dependency management" but migration to UV aligns with hypermodern principles (see justification below)

### Justification for Deviation

| Deviation | Why Needed | Simpler Alternative Rejected Because |
| ---------- | ---------- | ------------------------------------ |
| UV instead of Poetry for dependency management | UV is faster, more modern, and aligns with hypermodern Python best practices; spec requires migration in 5 stages | Keeping Poetry would maintain compatibility but contradicts the feature's goal of modernizing tooling; spec is explicit about this migration |

### Constitution Amendment Impact

This migration will require updating AGENTS.md to reflect UV as the dependency management tool, effectively amending the "Hypermodern Python Standards" section which currently references Poetry. This is a direct change to comply with the spec.

**Status**: AGENTS.md has been updated to include UV in Active Technologies and to reference UV in Pre-commit Hooks section (post-design amendment complete).

## Project Structure

### Documentation (this feature)

```text
specs/005-migrate-poetry-to-uv/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── cli.md           # CLI contract (if applicable)
└── checklists/
    └── requirements.md  # Migration checklist
```

### Source Code (repository root)

No structural changes to source code. Migration affects only tooling configuration files:

```text
# Modified Files (tooling only, no source structure changes)
.github/workflows/
├── tests.yml            # Stage 1: Replace Poetry with UV
└── release.yml          # Stage 1: Replace Poetry with UV

noxfile.py               # Stage 2: Replace nox-poetry with native nox + UV
pyproject.toml           # Stage 2: Remove nox-poetry dependency

src/ord_plan/            # Stage 3: Check for Poetry subprocess calls (expected: none)

tasks.py                 # Stage 4: Replace `poetry run` with `uv run`

README.md                # Stage 5: Update installation instructions
CONTRIBUTING.md          # Stage 5: Update setup instructions
AGENTS.md                # Stage 5: Update technology list
.pre-commit-config.yaml  # Stage 5: Replace `poetry run` with `uv run`
Dockerfile               # Stage 5: Update Dockerfile to use UV
docs/                    # Stage 5: Update any Poetry references
```

**Structure Decision**: This is a migration feature, not a new feature. The existing project structure (src/ord_plan/, tests/, docs/) remains unchanged. Only tooling configuration files are modified to replace Poetry with UV commands and configuration.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
| ---------- | ---------- | ------------------------------------ |
| UV instead of Poetry for dependency management | UV is faster, more modern, and aligns with hypermodern Python best practices; spec explicitly requires this migration | Keeping Poetry would maintain compatibility but contradicts the feature's goal of modernizing tooling; the spec is explicit about migrating to UV
