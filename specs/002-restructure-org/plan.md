# Implementation Plan: Repository Restructure

**Branch**: `002-restructure-org` | **Date**: 2025-12-17 | **Spec**: [Repository Restructure](./spec.md)
**Input**: Feature specification from `/specs/002-restructure-org/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Move Python package files from ord-plan/ subdirectory to repository root level while preserving all functionality, git history, and ensuring all development workflows continue to work identically. Use git mv operations for history preservation, systematic path updates for configuration files, and comprehensive testing to ensure zero regression.

## Technical Context

**Language/Version**: Python 3.7+ (as specified in pyproject.toml)
**Primary Dependencies**: Click (>=8.0.1), Poetry for dependency management
**Testing**: pytest with 100% coverage requirement
**Target Platform**: Linux/macOS/Windows (CLI tool)
**Project Type**: Repository refactoring (infrastructure operation)
**Git Operations**: git mv for history preservation
**File Movement**: Direct moves (no temporary directories)
**Path Resolution**: Systematic regex-based updates
**Import Strategy**: Remove ord_plan prefix after src/ move to root
**Validation**: Multi-step verification (imports, tests, linting)
**CLI Approach**: No new CLI commands - use refactoring scripts for one-time operation

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

### Required Constitution Compliance Gates

- **✅ CLI-First Design**: Repository refactoring is not a CLI feature - infrastructure operation using scripts
- **✅ Test-Driven Development**: TDD mandatory with 100% test coverage for any new validation scripts
- **✅ Org-Mode Native**: Not applicable - refactoring doesn't change output formats
- **✅ Template Generation Focus**: Not applicable - refactoring preserves existing functionality
- **✅ Hypermodern Python Standards**: All file operations and updates follow Python packaging standards
- **✅ Script-Based Approach**: Refactoring operations use scripts, not CLI commands, as this is a one-time infrastructure change

### Constitution Compliance Justification

This is a repository refactoring operation, not new functionality. It preserves all existing CLI-first design, org-mode native output, and template generation capabilities while moving files to standard Python project structure. All operations maintain Test-Driven Development principles with comprehensive validation, follow Hypermodern Python Standards for packaging, and ensure zero regression of existing functionality. The refactoring uses scripts rather than CLI commands as this is a one-time infrastructure change to reorganize the repository structure.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# CLI Tool Project Structure (ord-plan)
src/ord_plan/
├── __init__.py
├── __main__.py
├── cli/                 # Click command modules
│   ├── __init__.py
│   ├── generate.py      # Template generation commands
│   └── config.py        # Configuration handling
├── templates/           # Org-mode template definitions
│   ├── __init__.py
│   └── [template_type].py
├── parsers/            # Input/output format parsers
│   ├── __init__.py
│   ├── org_mode.py      # Org-mode parser/renderer
│   └── json_parser.py   # JSON output support
└── utils/
    ├── __init__.py
    └── validators.py    # Template validation logic

tests/
├── contract/           # CLI interface tests
├── integration/        # End-to-end template generation tests
└── unit/              # Individual component tests
    ├── test_cli/
    ├── test_templates/
    ├── test_parsers/
    └── test_utils/

docs/                  # Sphinx documentation
└── usage.md           # CLI usage examples
```

**Structure Decision**: Selected CLI tool structure maintained from existing ord-plan package. Repository restructuring moves this entire structure from ord-plan/ subdirectory to repository root, preserving all internal organization while achieving standard Python project layout.

## Complexity Tracking

> **No Constitution violations - all standards met with straightforward restructuring approach**

| Violation | Why Needed                                                                                   | Simpler Alternative Rejected Because |
| --------- | -------------------------------------------------------------------------------------------- | ------------------------------------ |
| None      | All constitution requirements satisfied through standard file operations and git mv commands | N/A                                  |
