# CLI Contract: Migrate from Poetry to UV

**Feature**: 005-migrate-poetry-to-uv | **Date**: 2025-12-23

## Overview

This document describes the contract for the Poetry to UV migration. Since this is a migration feature with no new CLI functionality, the contract focuses on preserving existing CLI behavior while replacing the underlying dependency management tool.

## Contract Statement

The migration MUST NOT change any CLI command behavior, output format, or user-facing functionality. The only changes are internal: replacing Poetry commands with UV equivalents.

## Preserved CLI Commands

All existing CLI commands remain unchanged:

```bash
# Template generation (unchanged)
ord-plan generate --input events.yaml --output schedule.org

# Output format (unchanged)
ord-plan generate --input events.yaml --output schedule.json --format json
```

## Developer Commands

Invoke commands remain the same, but use UV internally:

```bash
# Testing (uses uv run internally)
invoke pytest
invoke test-unit
invoke test-integration
invoke test-contract

# Linting (uses uv run internally)
invoke lint
invoke mypy
invoke black
invoke isort
invoke flake8
invoke darglint

# Pre-commit (uses uv run internally)
invoke pre-commit
invoke pre-commit-install
```

## Non-Functional Contract

### Performance

- **Requirement**: No performance regression
- **Acceptance**: UV should be faster than Poetry, but performance is not measured
- **Contract**: CLI commands must complete successfully, regardless of execution time

### Compatibility

- **Requirement**: Maintain backward compatibility for CLI interface
- **Acceptance**: All existing CLI commands work exactly as before
- **Contract**: No changes to command-line arguments, options, or output format

### Testing

- **Requirement**: All tests must pass after migration
- **Acceptance**: 100% test pass rate maintained
- **Contract**: Test coverage remains the same; no new tests required for migration

## Migration Guarantees

### What Changes

- Poetry installation in GitHub workflows → UV installation
- `poetry run` in invoke tasks → `uv run`
- `poetry build` in release workflow → `uv build`
- Version detection using Poetry → Custom Python script
- nox-poetry plugin → Native nox with UV
- Poetry documentation → UV documentation

### What Does NOT Change

- CLI command names and arguments
- CLI output format (org-mode, JSON)
- Test suite behavior
- Template generation logic
- User-facing functionality

## Contract Violations

A migration stage fails the contract if:

1. Any CLI command changes behavior
2. Any test fails
3. Output format changes
4. Command-line interface changes
5. New dependencies are added to the core package (only tooling changes allowed)

## Verification Methods

### Automated Verification

```bash
# Run all tests
invoke pytest

# Run all linting
invoke lint

# Test CLI commands
ord-plan generate --input tests/fixtures/sample_events.yaml --output /tmp/test.org

# Verify no Poetry in source code
grep -r "poetry" src/ --exclude-dir=__pycache__  # Should find nothing
```

### Manual Verification

- Read through documentation to ensure accuracy
- Test all invoke tasks
- Verify GitHub Actions pass
- Check Dockerfile builds successfully

## Sign-Off

Migration is complete when:
- [ ] All 5 stages are implemented
- [ ] All tests pass (`invoke pytest`)
- [ ] All linting passes (`invoke lint`)
- [ ] GitHub Actions pass on all platforms
- [ ] No Poetry commands remain in any files
- [ ] Documentation references UV only
- [ ] Developer can clone repo and run `uv pip install -e ".[dev]"`
