# Quickstart Guide: Repository Restructure

**Date**: 2025-12-17  
**Purpose**: Quick guide for performing repository restructuring operations

## Prerequisites

### Repository Requirements
- Clean git working directory (no uncommitted changes)
- Git repository initialized
- ord-plan/ subdirectory exists with Python package structure
- Sufficient filesystem permissions for file operations

### Tool Requirements
- Git (for history preservation)
- Python 3.7+ (for import validation)
- Python package management tools (Poetry recommended)

## Quick Start

### 1. Basic Restructuring

```bash
# Navigate to repository root
cd /path/to/ord-plan

# Run restructuring with validation
ord-plan restructure

# Alternative: Preview changes first
ord-plan restructure --dry-run
```

### 2. Manual Restructuring (Step-by-Step)

If you prefer manual control over the process:

#### Step 1: Move Source Code
```bash
# Move Python source code preserving history
git mv -v ord-plan/src/* ./
git commit -m "Move src to repository root"
```

#### Step 2: Move Test Suite
```bash
# Move test directory preserving history
git mv -v ord-plan/tests/* ./
git commit -m "Move tests to repository root"
```

#### Step 3: Move Documentation and Config
```bash
# Move documentation
git mv -v ord-plan/docs/* ./

# Move project metadata files
git mv -v ord-plan/README.md ./
git mv -v ord-plan/LICENSE ./
git mv -v ord-plan/pyproject.toml ./
git mv -v ord-plan/.github/* ./.github/

# Commit all moves
git add .
git commit -m "Move docs and metadata to repository root"
```

#### Step 4: Update Python Imports
```bash
# Update all Python imports to remove ord_plan prefix
find . -name "*.py" -exec sed -i 's/from ord_plan\./from /g' {} +
find . -name "*.py" -exec sed -i 's/import ord_plan\./import /g' {} +
```

#### Step 5: Update Configuration Files
```bash
# Update pyproject.toml paths
sed -i 's/ord-plan\///g' pyproject.toml
sed -i 's/src\///g' pyproject.toml

# Update test imports
find tests/ -name "*.py" -exec sed -i 's/ord_plan\///g' {} +
```

#### Step 6: Validate and Commit
```bash
# Run tests to verify functionality
python -m pytest tests/

# Run linting
ruff check .

# Commit all updates
git add .
git commit -m "Update paths and imports after restructuring"
```

## Validation Checklist

### Pre-Restructuring Validation
- [ ] Git working directory is clean (`git status` shows no changes)
- [ ] ord-plan/ directory exists with expected structure
- [ ] All tests currently pass (`python -m pytest ord-plan/tests/`)
- [ ] Repository has no untracked files that should be committed

### Post-Restructuring Validation
- [ ] All files moved successfully (no data loss)
- [ ] Python imports work correctly (`python -c "import cli, models"`)
- [ ] Test suite passes (`python -m pytest tests/`)
- [ ] Linting passes (`ruff check .`)
- [ ] Package discovery works (`python -c "import setuptools"`)
- [ ] Git history preserved for moved files

## Common Issues and Solutions

### Import Errors After Restructuring
**Problem**: `ModuleNotFoundError: No module named 'cli'`
**Solution**: Update imports in all Python files to remove ord_plan prefix

### Test Failures
**Problem**: Tests can't find modules after restructuring
**Solution**: Update test imports and check conftest.py for path references

### Configuration File Issues
**Problem**: Build tools can't find files
**Solution**: Update all path references in pyproject.toml and workflow files

### Git History Loss
**Problem**: Files lose history after move
**Solution**: Use `git mv` instead of manual copy/delete operations

## Troubleshooting

### Debug Mode
```bash
# Use verbose output for detailed operation information
ord-plan restructure --verbose

# Dry run to preview changes
ord-plan restructure --dry-run --verbose
```

### Recovery
If restructuring fails, you can recover using git:

```bash
# Reset to last known good state
git reset --hard HEAD~1

# Or stash changes and start over
git stash
git stash pop
```

## Best Practices

### Before Restructuring
1. **Backup**: Create a backup branch before starting
2. **Clean State**: Ensure git working directory is clean
3. **Baseline**: Run full test suite to establish baseline

### During Restructuring
1. **Small Steps**: Move and validate in small increments
2. **History Preservation**: Always use git mv for file moves
3. **Immediate Testing**: Test after each major change

### After Restructuring
1. **Comprehensive Testing**: Run full test suite, linting, and build
2. **Documentation Update**: Update any documentation that references old structure
3. **Team Communication**: Notify team of structural changes

## Integration with Development Workflow

### CI/CD Updates
After restructuring, update CI/CD workflows to:
- Remove `cd ord-plan` or working-directory steps
- Update file paths for linting and testing
- Adjust artifact collection paths

### IDE Configuration
Update IDE settings to recognize new project structure:
- Python interpreter path
- Source root configuration
- Test discovery settings

### Team Onboarding
Update onboarding documentation to reflect new:
- Repository structure
- Development setup instructions
- Common development commands