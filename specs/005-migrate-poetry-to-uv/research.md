# Research: Migrate from Poetry to UV

**Feature**: 005-migrate-poetry-to-uv | **Date**: 2025-12-23

## Overview

This research document consolidates technical decisions for migrating the ord-plan codebase from Poetry to UV for dependency management. The migration is divided into 5 stages: GitHub workflows, noxfile.py, source code, tasks.py, and documentation.

## UV Command Mappings

### Poetry to UV Command Equivalents

| Poetry Command | UV Equivalent | Notes |
| -------------- | ------------ | ----- |
| `poetry run <command>` | `uv run <command>` | Direct replacement for running commands in virtual environment |
| `poetry install` | `uv pip install -e .` | Install package in editable mode |
| `poetry install --with dev` | `uv pip install -e ".[dev]"` | Install with optional dependencies |
| `poetry build` | `uv build` | Build package for distribution |
| `poetry version` | Custom Python script | See version detection below |
| `poetry self add poetry-plugin-export` | Not needed | UV has built-in support |

### Nox-Poetry to Native Nox + UV

| nox-poetry Pattern | UV Replacement | Notes |
| ------------------ | ------------- | ----- |
| `from nox_poetry import Session` | `from nox import Session` | Use native nox imports |
| `session.poetry.export_requirements()` | `session.run("uv", "pip", "freeze", f"--output={requirements}", external=True)` | Export requirements using UV |
| `session.install(".")` (with nox-poetry) | `session.run("uv", "pip", "install", ".", external=True)` or `session.install(".")` | Both work; UV is faster |

## Version Detection with UV

### Poetry Version Detection

```bash
poetry version | awk '{ print $2 }'
```

### UV Version Detection

```bash
uv run python -c "import tomli; print(tomli.load(open('pyproject.toml'))['project']['version'])"
```

**Decision**: Use UV with tomli for version detection. Requires:
- `uv run` for execution
- `tomli` package (already in dependencies)
- Access to pyproject.toml file

**Rationale**: Direct Python access to pyproject.toml is reliable and doesn't depend on Poetry-specific commands. The tomli library is already in the project dependencies.

### Version Bumping with UV

Poetry's `poetry version patch` and `poetry version <version>` commands don't have direct UV equivalents since Poetry manages versions differently.

**Decision**: Use Python script with tomli and tomli_w for version manipulation.

```python
import tomli, re

data = tomli.load(open('pyproject.toml'))
version = data['project']['version']
parts = version.split('.')
parts[-1] = str(int(parts[-1]) + 1)
new_version = '.'.join(parts)
data['project']['version'] = f'{new_version}.dev.$(date +%s)'

with open('pyproject.toml', 'w') as f:
    import tomli_w
    tomli_w.dump(data, f)
```

**Rationale**: This gives fine-grained control over version manipulation and doesn't depend on Poetry's version management. The tomli_w library will need to be added to dependencies.

## Installation Methods

### Poetry Installation (Current)

```bash
pipx install poetry
```

### UV Installation (Target)

```bash
pipx install uv
```

**Decision**: Both Poetry and UV are installed via pipx, making the migration straightforward in GitHub workflows.

**Rationale**: pipx is the standard tool for installing Python CLI applications in isolated environments. UV installation follows the same pattern as Poetry.

## GitHub Workflow Changes

### Tests Workflow

**Current (Poetry)**:
```yaml
- name: Install Poetry
  run: |
    pipx install --pip-args=--constraint=.github/workflows/constraints.txt poetry
    poetry self add poetry-plugin-export
    poetry --version

- name: Install Nox
  run: |
    pipx install --pip-args=--constraint=.github/workflows/constraints.txt nox
    pipx inject --pip-args=--constraint=.github/workflows/constraints.txt nox nox-poetry
    nox --version
```

**Target (UV)**:
```yaml
- name: Install UV
  run: |
    pipx install --pip-args=--constraint=.github/workflows/constraints.txt uv
    uv --version

- name: Install Nox
  run: |
    pipx install --pip-args=--constraint=.github/workflows/constraints.txt nox
    nox --version
```

**Decision**: Direct replacement of Poetry with UV; remove nox-poetry injection.

**Rationale**: UV provides equivalent functionality without the need for the nox-poetry plugin. Native nox with UV commands is the recommended approach.

### Release Workflow

**Current (Poetry)**:
```yaml
- name: Install Poetry
  run: |
    pipx install --pip-args=--constraint=.github/workflows/constraints.txt poetry
    poetry --version

- name: Bump version for developmental release
  run: |
    poetry version patch &&
    version=$(poetry version | awk '{ print $2 }') &&
    poetry version $version.dev.$(date +%s)

- name: Build package
  run: |
    poetry build --ansi
```

**Target (UV)**:
```yaml
- name: Install UV
  run: |
    pipx install --pip-args=--constraint=.github/workflows/constraints.txt uv
    uv --version

- name: Bump version for developmental release
  run: |
    python -c "
    import tomli, re
    data = tomli.load(open('pyproject.toml'))
    version = data['project']['version']
    parts = version.split('.')
    parts[-1] = str(int(parts[-1]) + 1)
    new_version = '.'.join(parts)
    data['project']['version'] = f'{new_version}.dev.$(date +%s)'
    with open('pyproject.toml', 'w') as f:
        import tomli_w
        tomli_w.dump(data, f)
    "

- name: Build package
  run: |
    uv build
```

**Decision**: Use custom Python script for version manipulation; UV for package building.

**Rationale**: UV doesn't have built-in version management commands like Poetry. Using tomli/tomli_w provides direct control over pyproject.toml.

## Noxfile Changes

### Import Changes

**Current (nox-poetry)**:
```python
try:
    from nox_poetry import Session
    from nox_poetry import session
except ImportError:
    message = f"""\
    Nox failed to import the 'nox-poetry' package.

    Please install it using the following command:

    {sys.executable} -m pip install nox-poetry"""
    raise SystemExit(dedent(message)) from None
```

**Target (Native Nox)**:
```python
from nox import Session
from nox import session
```

**Decision**: Remove nox-poetry imports and error handling; use native nox.

**Rationale**: nox-poetry is no longer needed with UV. Native nox provides the same functionality when combined with UV commands.

### Safety Session Changes

**Current (nox-poetry)**:
```python
@session(python=python_versions)
def safety(session: Session) -> None:
    """Scan dependencies for insecure packages."""
    requirements = session.poetry.export_requirements()
    session.install("safety")

    result = session.run(
        "safety",
        "scan",
        "--full-report",
        f"--file={requirements}",
        "--disable-requirement-checks",
        success_codes=[0, 64],
        silent=True,
    )
```

**Target (UV)**:
```python
@session(python=python_versions)
def safety(session: Session) -> None:
    """Scan dependencies for insecure packages."""
    requirements = session.create_tmp()
    session.run("uv", "pip", "freeze", f"--output={requirements}", external=True)
    session.install("safety")

    result = session.run(
        "safety",
        "scan",
        "--full-report",
        f"--file={requirements}",
        "--disable-requirement-checks",
        success_codes=[0, 64],
        silent=True,
    )
```

**Decision**: Use `uv pip freeze` to export requirements.

**Rationale**: UV's `pip freeze` command provides equivalent functionality to nox-poetry's export_requirements method.

### Session Installation

**Current (nox-poetry)**:
```python
session.install(".", "pytest", "coverage")
```

**Target (UV)**:
```python
session.run("uv", "pip", "install", ".", "pytest", "coverage", external=True)
# OR (both work, UV is faster):
session.install(".", "pytest", "coverage")
```

**Decision**: Use `session.install()` for simplicity, optionally `uv pip install` for speed.

**Rationale**: Nox's native `session.install()` works fine with UV installed in the environment. For better performance, explicitly using `uv pip install` is preferred.

## Tasks.py Changes

### Poetry Run to UV Run

**Current**:
```python
@task
def pytest(c):
    """Run pytest tests."""
    setup_python_path()
    return run_command(
        c,
        "poetry run pytest tests/ -v --cov=ord_plan --cov-report=term-missing -W ignore::DeprecationWarning",
        "Running pytest tests",
    )
```

**Target**:
```python
@task
def pytest(c):
    """Run pytest tests."""
    setup_python_path()
    return run_command(
        c,
        "uv run pytest tests/ -v --cov=ord_plan --cov-report=term-missing -W ignore::DeprecationWarning",
        "Running pytest tests",
    )
```

**Decision**: Replace all `poetry run` with `uv run`.

**Rationale**: Direct string replacement maintains the same command structure while switching the dependency manager.

## Documentation Changes

### README.md

**Current**: Poetry as installation method
**Target**: UV as recommended method; remove Poetry references

**Decision**: Prioritize UV; remove Poetry installation sections.

**Rationale**: UV is the modern, recommended tool. Poetry references should be removed to avoid confusion.

### AGENTS.md

**Current**: Poetry listed in Active Technologies
**Target**: UV replaces Poetry in Active Technologies

**Decision**: Update technology list to reflect UV as dependency manager.

**Rationale**: This is a source of truth for the project's technology stack. It must reflect the actual tool in use.

## pyproject.toml Considerations

### Poetry Sections

If the pyproject.toml contains `[tool.poetry]` sections, they should be removed:

```toml
# REMOVE:
[tool.poetry]
name = "ord-plan"
version = "0.0.1"
description = "..."
authors = ["..."]

[tool.poetry.dependencies]
python = "^3.7"
click = "^8.0.1"

[tool.poetry.dev-dependencies]
pytest = "..."
...

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

# REPLACE with standard PEP 621 sections (if not already present):
[project]
name = "ord-plan"
version = "0.0.1"
description = "..."
dependencies = [
    "click>=8.0.1",
]

[project.optional-dependencies]
dev = [
    "pytest",
    ...
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Decision**: Check if pyproject.toml still uses Poetry sections; remove them if present.

**Rationale**: The project should use standard PEP 621 sections after migration. Note: The spec mentions uv.lock already exists, suggesting the pyproject.toml may already be migrated.

## Dependencies to Add

### tomli_w

The version bumping script requires `tomli_w` for writing pyproject.toml:

```bash
uv pip install tomli_w
```

Add to `pyproject.toml`:
```toml
[project.optional-dependencies]
dev = [
    ...
    "tomli-w>=1.0.0",
]
```

**Decision**: Add tomli-w to dev dependencies.

**Rationale**: Required for writing to pyproject.toml during version bumping in release workflow.

## Rollback Strategy

If any migration stage fails:

1. Restore modified files from git
2. Reinstall nox-poetry if Stage 2 failed
3. Restart migration from Stage 1

**Decision**: Fail-fast approach; each stage must pass completely before proceeding.

**Rationale**: Ensures a working state at all times. Git provides easy rollback capability.

## Performance Considerations

### UV vs Poetry Performance

UV is generally faster than Poetry for:
- Dependency resolution
- Package installation
- Virtual environment creation

However, the spec explicitly states: "Performance is not a critical requirement; UV is expected to be faster but we just need tests to pass."

**Decision**: Do not add performance tests or benchmarks.

**Rationale**: Functional correctness is the only requirement. Performance improvements are a side benefit, not a formal requirement.

## Summary of Decisions

1. **Command Mapping**: Direct replacement of `poetry run` with `uv run`
2. **Version Detection**: Use Python with tomli instead of Poetry version commands
3. **Noxfile**: Remove nox-poetry imports; use native nox with UV commands
4. **GitHub Workflows**: Replace Poetry installation with UV; remove nox-poetry injection
5. **Documentation**: Remove Poetry references; update to UV commands
6. **Dependencies**: Add tomli-w to dev dependencies
7. **Rollback**: Git-based rollback for each stage
8. **Performance**: No performance tests; focus on functional correctness

## Alternatives Considered

### Alternative 1: Keep Poetry alongside UV

Rejected because:
- Increases confusion about which tool to use
- Adds maintenance burden for two package managers
- Spec requires complete migration to UV

### Alternative 2: Use pip instead of UV

Rejected because:
- UV is specified in the feature spec
- UV provides better dependency resolution than pip
- UV is faster and more modern

### Alternative 3: Use Poetry-based version management

Rejected because:
- Requires keeping Poetry installed
- Defeats the purpose of migration
- Custom Python script gives more control

### Alternative 4: Remove nox entirely

Rejected because:
- Scope creep; this is a future stage (Stage 7)
- Current migration focuses only on replacing Poetry
- Keeping nox maintains developer familiarity
