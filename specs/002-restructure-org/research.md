# Research Findings: Repository Restructure

**Date**: 2025-12-17
**Purpose**: Research for repository restructuring from ord-plan/ subdirectory to repository root

## File Movement and Git Operations

**Decision**: Use git mv commands to preserve history
**Rationale**: Preserves complete file history while using standard git operations. More reliable than filter-repo for this use case.
**Alternatives considered**:

- git filter-repo: More complex, overkill for simple directory moves
- Manual copy/add/delete: Loses history, not recommended

## Python Import Resolution

**Decision**: Update imports to remove ord_plan prefix after moving src/ to root
**Rationale**: After moving src/ to root, the package structure changes and imports must be updated accordingly.
**Alternatives considered**:

- Keep ord_plan as top-level package: Would require maintaining nested structure
- Use relative imports: Could break 在不同目录中

## Configuration File Updates

**Decision**: Systematic update of all configuration files to remove ord-plan/ prefixes
**Rationale**: All build tools, linters, and test runners need updated paths to work with new structure.
**Alternatives considered**:

- Update only critical files: Risk of breaking workflows
- Use environment variables: Overcomplication for simple path changes

## Test Structure Handling

**Decision**: Maintain tests/fixtures/ structure while updating test imports
**Rationale**: AGENTS.md requires all test fixtures remain in tests/fixtures/ directory. Only imports need updating.
**Alternatives considered**:

- Move fixtures: Violates constitution requirements
- Use absolute paths: Reduces portability

## CI/CD Workflow Updates

**Decision**: Remove working-directory references and update all paths
**Rationale**: GitHub Actions workflows need to operate from repository root after restructuring.
**Alternatives considered**:

- Keep working-directory: Would require maintaining ord-plan/ structure
- Use conditional logic: Unnecessary complexity

## Validation Approach

**Decision**: Multi-step verification (imports, tests, linting, package discovery)
**Rationale**: Ensures all aspects of repository functionality work correctly after changes.
**Alternatives considered**:

- Test only one aspect: Risk of missing breakage
- Skip validation: High risk of broken repository

## Implementation Commands Summary

```bash
# Core file moves
git mv -v ord-plan/src/* ./
git mv -v ord-plan/tests/* ./

# Import updates
find . -name "*.py" -exec sed -i 's/from ord_plan\./from /g' {} +

# Configuration updates
sed -i 's/ord-plan\///g' pyproject.toml
sed -i 's/src\///g' pyproject.toml

# Test updates
find tests/ -name "*.py" -exec sed -i 's/ord_plan\///g' {} +

# Verification
python -m pytest tests/
ruff check .
```

All research complete - no NEEDS CLARIFICATION items remain.
