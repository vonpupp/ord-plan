# ord-plan Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-12-17

## Active Technologies

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

pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES]
ruff check .

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

### File Management Rules

**NO TEST FILES IN PROJECT ROOT**: Test and debug files MUST be created only in `tests/fixtures/` directory or `tmp/` directories. Never create test files in the project root directory. Any test files outside designated locations must be immediately removed.

- **Fixtures Location**: All test data belongs in `tests/fixtures/` using proper naming conventions
- **Temporary Files**: Quick tests may use `/tmp/` or project's temporary directories
- **Clean Up Required**: Any test/debug files created during development must be removed before commits
- **Exception**: Files in `tests/fixtures/` are version-controlled and intended for testing

## Recent Changes

- 001-generate-org: Added Python 3.7+ (as specified in pyproject.toml) + Click (>=8.0.1), Poetry for dependency management
- Added constitutional amendment: No performance testing - focus on functionality over performance metrics

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
