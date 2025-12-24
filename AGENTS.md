# ord-plan Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-12-18

## Active Technologies
- Python 3.7+ (as specified in pyproject.toml) + Click (>=8.0.1), PyYAML, Poetry for dependency management (004-add-format-flag)
- Files (YAML configuration and org-mode output) (004-add-format-flag)
- Python 3.7+ (as specified in pyproject.toml) + Click (>=8.0.1), PyYAML, UV for dependency management (migrating from Poetry) (005-migrate-poetry-to-uv)
- Files (template generation output - org-mode and JSON) (005-migrate-poetry-to-uv)

- Python 3.7+ (as specified in pyproject.toml) + Click (>=8.0.1), Poetry for dependency management (001-generate-org)

## Project Structure

```text
src/
ord_plan/
tests/
docs/
.github/
```

## Commands

invoke [SINGLE AUTHORIZED TESTING COMMAND]
ruff check .

### Common Invoke Commands:

- `invoke pytest` - Run all tests with coverage
- `invoke lint` - Run all linting checks (black, isort, flake8, mypy, darglint)
- `invoke install-hooks` - Install pre-commit and git hooks
- `invoke install-hooks --use-symlinks` - Install hooks as symlinks instead of copying
- `invoke pre-commit` - Run all pre-commit hooks on all files
- `invoke help` - Show detailed usage examples
- `invoke --list` - List all available tasks

## Code Style

Python 3.7+ (as specified in pyproject.toml): Follow standard conventions

### flake8 Standards

All code MUST pass flake8 linting with the following objective standards:

**Line Length (B950)**: Maximum 88 characters per line

- All lines must be 88 characters or less
- Use line continuations, string concatenation, or parameter unpacking for longer lines

**Docstring Style (D codes)**: Follow PEP 257 docstring conventions

- D212: Multi-line docstring summary must start at first line
- D200: One-line docstring must fit on one line with quotes
- D105: Magic methods must have docstrings
- Other PEP 257 violations are not allowed

**Import Organization**: All imports must follow proper order and structure

- Standard library imports first
- Third-party imports second
- Local imports third
- One import per line, grouped by type
- Use isort for automatic formatting

**Exception Handling (B014)**: No redundant exception types

- Use base exception class instead of redundant combinations
- `except OSError:` instead of `except (OSError, PermissionError):`

**Unused Variables (B007, F401, F841)**: No unused variables or imports

- Use underscore prefix for intentionally unused variables
- Remove unused imports and assignments
- Fix F821 undefined name errors

**Variable Usage (B907)**: Use proper string formatting

- Use `!r` conversion flag instead of manual quotes
- Prefer f-strings with proper formatting

**Security (S codes)**: Follow secure coding practices

- Use absolute paths for subprocess calls (S607)
- Validate subprocess inputs (S603)
- Consider subprocess security implications (S404)
- Use secure temp file handling (S108, S103)

**Complexity (C901)**: Maintain reasonable function complexity

- Functions should be under 10 complexity rating
- Break complex functions into smaller functions
- Reduce nested logic and control flow

## Testing Patterns

All test data MUST be centralized in `tests/fixtures/` directory. Use the fixture helper functions in `tests/fixtures.py`:

- `get_fixture_path(filename)` - Get absolute path to fixture file
- `read_fixture(filename)` - Read fixture contents as string
- `write_to_fixture(filename, content)` - Write temporary fixtures
- `list_fixtures()` - List all available fixture files

Fixture naming convention: `test_{purpose}_{scenario}.{ext}` (e.g., `test_rules_basic.yaml`, `existing_content.org`).

No inline test data or scattered test files allowed in the codebase.

### File Management Rules

**NO TEST FILES IN PROJECT ROOT**: Test and debug files MUST be created only in `tests/fixtures/` directory or `tmp/` directories. Never create test files in the project root directory. Any test files outside designated locations must be immediately removed.

- **Fixtures Location**: All test data belongs in `tests/fixtures/` using proper naming conventions
- **Temporary Files**: Quick tests may use `/tmp/` or project's temporary directories
- **Clean Up Required**: Any test/debug files created during development must be removed before commits
- **Exception**: Files in `tests/fixtures/` are version-controlled and intended for testing

## Pre-commit Hooks

Pre-commit hooks provide automated code quality checks before commits. They ensure consistent code style and catch common issues early.

### Installation

Install pre-commit hooks and git hooks using invoke:

```bash
invoke install-hooks  # Install pre-commit framework and project git hooks
```

### Manual Usage

Run all pre-commit hooks manually on all files:

```bash
invoke pre-commit
```

Or run directly with uv:

```bash
uv run pre-commit run --all-files
```

### Individual Hook Commands

You can also run individual checks manually:

- `invoke black` - Black formatting check
- `invoke isort` - Import sorting check
- `invoke flake8` - Flake8 linting
- `invoke mypy` - Type checking
- `invoke darglint` - Docstring linting (manual stage only)

### Hook Configuration

Pre-commit hooks are configured in `.pre-commit-config.yaml` and use uv to ensure all tools run in the correct virtual environment. The hooks include:

- **Formatting**: Black, isort
- **Linting**: Flake8, darglint, mypy
- **File checks**: End-of-file-fixer, trailing-whitespace, check-added-large-files
- **Config validation**: check-toml, check-yaml
- **Code modernization**: pyupgrade

### Pre-commit vs Invoke

- **Pre-commit hooks**: Run automatically before commits, focus on file-level changes
- **Invoke tasks**: Run manually, provide comprehensive project-wide checks and testing
- **Both methods** use the same underlying tools and configuration for consistency

## Recent Changes
- 2025-12-24: Added git-hooks/ directory with install-hooks task for managing git hooks
- 005-migrate-poetry-to-uv: Added Python 3.7+ (as specified in pyproject.toml) + Click (>=8.0.1), PyYAML, UV for dependency management (migrating from Poetry)
- 004-add-format-flag: Added Python 3.7+ (as specified in pyproject.toml) + Click (>=8.0.1), PyYAML, Poetry for dependency management

- 001-generate-org: Added Python 3.7+ (as specified in pyproject.toml) + Click (>=8.0.1), Poetry for dependency management

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
