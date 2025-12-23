# Implementation Plan: Add Format Flag for Configuration Decoupling

**Branch**: `004-add-format-flag` | **Date**: 2025-12-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-add-format-flag/spec.md`

## Summary

Add a new `--format` command-line flag to the `ord-plan generate` command that allows users to specify a separate YAML file containing only formatting configuration options (REVERSE_DATETREE_WEEK_FORMAT, REVERSE_DATETREE_DATE_FORMAT, REVERSE_DATETREE_YEAR_FORMAT, REVERSE_DATETREE_USE_WEEK_TREE). The tool will merge formatting options from the format file with event definitions from the rules file, with format file options taking precedence over rules file options. This enables configuration reuse and cleaner separation of concerns while maintaining backward compatibility with existing combined rules files.

## Technical Context

**Language/Version**: Python 3.7+ (as specified in pyproject.toml)
**Primary Dependencies**: Click (>=8.0.1), PyYAML, Poetry for dependency management
**Storage**: Files (YAML configuration and org-mode output)
**Testing**: pytest with 100% coverage requirement for new code paths
**Target Platform**: Linux/macOS/Windows (CLI tool)
**Project Type**: Single (CLI tool - determines source structure)
**Performance Goals**: <2 seconds for typical template generation (<1000 lines)
**Constraints**: <50MB memory usage, streaming-friendly output for large templates
**Scale/Scope**: Template generation tool supporting org-mode and JSON output formats

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

**Post-Design Status**: ✅ All gates pass after Phase 1 design (2025-12-23)

### Required Constitution Compliance Gates

- **✅ CLI-First Design**: Feature MUST be accessible via command-line interface
  - New `--format` flag adds to existing CLI interface
  - Follows Click conventions for optional flags

- **✅ Test-Driven Development**: TDD mandatory with 100% test coverage
  - All new code paths require tests first
  - Test fixtures in `tests/fixtures/` directory
  - Use `invoke pytest` for testing

- **✅ Org-Mode Native**: Primary output format MUST be org-mode compliant
  - Output format unchanged, only configuration mechanism changes
  - Existing org-mode rendering logic preserved

- **✅ Template Generation Focus**: Functionality MUST support template generation
  - Feature enables configuration reuse for template generation
  - Core template generation functionality unchanged

- **✅ Hypermodern Python Standards**: MUST follow cookiecutter conventions (Poetry, Black, mypy, etc.)
  - Code uses existing type hints and dataclass patterns
  - Follows established file structure and naming conventions

## Project Structure

### Documentation (this feature)

```text
specs/004-add-format-flag/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── cli.md           # CLI interface contract
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# CLI Tool Project Structure (ord-plan)
src/ord_plan/
├── __init__.py
├── __main__.py
├── cli/                 # Click command modules
│   ├── __init__.py
│   ├── config.py        # Configuration handling (MODIFY)
│   └── generate.py      # Template generation commands (MODIFY)
├── models/              # Data models
│   ├── __init__.py
│   ├── event_rule.py    # Event rule definition
│   └── org_event.py     # Org-mode event representation
├── parsers/             # Input/output format parsers
│   ├── __init__.py
│   ├── org_mode.py      # Org-mode parser/renderer
│   └── yaml_parser.py   # YAML output support (MODIFY)
└── utils/               # Utility functions
    ├── __init__.py
    └── validators.py    # Template validation logic

tests/
├── contract/            # CLI interface tests (ADD TESTS)
├── integration/          # End-to-end template generation tests (ADD TESTS)
└── unit/                # Individual component tests (ADD TESTS)
    └── test_parsers/    # YAML parser tests (ADD TESTS)

docs/                     # Sphinx documentation
└── usage.md             # CLI usage examples (UPDATE)
```

**Structure Decision**: Existing CLI tool structure with minor modifications. Changes concentrated in:
- `cli/generate.py`: Add `--format` option parameter and parsing logic
- `cli/config.py`: Add method to merge format file configuration with rules file configuration
- `parsers/yaml_parser.py`: Add validation for format-only files and merge logic
- Test fixtures in `tests/fixtures/` for format file validation

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation                  | Why Needed         | Simpler Alternative Rejected Because |
| -------------------------- | ------------------ | ------------------------------------ |
| [e.g., 4th project]        | [current need]     | [why 3 projects insufficient]        |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient]  |
