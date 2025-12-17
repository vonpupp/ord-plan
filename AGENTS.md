# ord-plan Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-12-16

## Active Technologies

- Python 3.7+ (as specified in pyproject.toml) + Click (>=8.0.1), Poetry for dependency management (001-generate-org)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.7+ (as specified in pyproject.toml): Follow standard conventions

## Testing Patterns

All test data MUST be centralized in `tests/fixtures/` directory. Use the fixture helper functions in `tests/fixtures.py`:
- `get_fixture_path(filename)` - Get absolute path to fixture file
- `read_fixture(filename)` - Read fixture contents as string
- `write_to_fixture(filename, content)` - Write temporary fixtures
- `list_fixtures()` - List all available fixture files

Fixture naming convention: `test_{purpose}_{scenario}.{ext}` (e.g., `test_rules_basic.yaml`, `existing_content.org`).

No inline test data or scattered test files allowed in the codebase.

## Recent Changes

- 001-generate-org: Added Python 3.7+ (as specified in pyproject.toml) + Click (>=8.0.1), Poetry for dependency management

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
