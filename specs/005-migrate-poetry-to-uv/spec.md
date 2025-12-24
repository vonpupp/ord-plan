# Feature Specification: Migrate from Poetry to UV

**Feature Branch**: `005-migrate-poetry-to-uv`
**Created**: 2025-12-23
**Status**: Draft
**Input**: User description: "Migrate from Poetry to UV across the ord-plan codebase in 5 stages: 1) GitHub workflows, 2) noxfile.py, 3) Source code, 4) tasks.py, 5) Documentation and cleanup"

## Clarifications

### Session 2025-12-23
- Q: What are the performance requirements for UV compared to Poetry (e.g., specific speedup targets, memory usage limits)? → A: Performance is not a critical requirement; UV is expected to be faster but we just need tests to pass
- Q: What backward compatibility window is required for Poetry usage after migration completes? → A: Allow immediate UV usage; no explicit backward compatibility window required for Poetry after Stage 5 complete
- Q: What should happen if a migration stage fails during execution? → A: Fail entire migration if any stage fails; start over from beginning
- Q: How should Poetry virtual environments be handled after migration? → A: Provide explicit cleanup commands for Poetry venvs after Stage 5
- Q: What is the preferred method for version detection in release workflow? → A: Use `python -c "import tomli; print(tomli.load(open('pyproject.toml'))['project']['version'])"` for simple version extraction

## User Scenarios & Testing _(mandatory)_

### User Story 1 - GitHub Actions CI/CD with UV (Priority: P1)

Replace Poetry installation and commands with UV equivalents in GitHub workflow files to enable CI/CD to run tests using UV dependency management instead of Poetry.

**Why this priority**: CI/CD changes are isolated from local development and allow early verification of the migration approach without affecting developer workflows. This is the lowest-risk starting point.

**Independent Test**: GitHub Actions workflows run successfully with UV installed and commands execute properly. Tests pass on all platforms (ubuntu-latest, windows-latest, macos-latest).

**Acceptance Scenarios**:

1. **Given** a modified `.github/workflows/tests.yml` with UV instead of Poetry, **When** a commit is pushed, **Then** all test sessions pass without Poetry-related errors
2. **Given** a modified `.github/workflows/release.yml` with UV instead of Poetry, **When** a release is triggered, **Then** version detection, building, and publishing work correctly
3. **Given** coverage artifact upload, **When** coverage data is combined, **Then** coverage reports are generated successfully using UV

---

### User Story 2 - Nox Sessions with UV (Priority: P2)

Update noxfile.py to use UV for dependency management instead of nox-poetry plugin, maintaining compatibility with existing nox sessions.

**Why this priority**: Nox is used for local testing and CI. Replacing nox-poetry with UV removes a Poetry dependency while keeping the nox workflow familiar to developers.

**Independent Test**: All nox sessions (pre-commit, mypy, tests, typeguard, xdoctest, docs-build) run successfully when invoked locally with `nox` command.

**Acceptance Scenarios**:

1. **Given** noxfile.py imports nox-poetry, **When** imports are replaced with native nox and UV commands, **Then** nox sessions execute without import errors
2. **Given** `session.poetry.export_requirements()` call, **When** replaced with `uv pip freeze`, **Then** safety session scans dependencies correctly
3. **Given** nox sessions install dependencies, **When** using `session.run("uv", "pip", "install", ...)`, **Then** all session dependencies are installed correctly

---

### User Story 3 - Source Code Commands Use UV (Priority: P3)

Replace any Poetry commands directly used in source code with UV equivalents, ensuring no runtime dependencies on Poetry remain.

**Why this priority**: Source code may invoke Poetry commands through subprocess or similar mechanisms. Ensuring all code uses UV prevents runtime Poetry dependencies.

**Independent Test**: All Python source files execute correctly without Poetry installed, using UV for any subprocess invocations.

**Acceptance Scenarios**:

1. **Given** any Python files with Poetry subprocess calls, **When** replaced with UV equivalents, **Then** the code executes without errors
2. **Given** no Poetry-specific code in source directory, **When** searching for "poetry" in src/, **Then** only documentation or comments remain

---

### User Story 4 - Invoke Tasks Use UV (Priority: P4)

Update tasks.py to use UV instead of Poetry for all invoke task commands, ensuring local development commands work with UV.

**Why this priority**: Invoke tasks are the primary interface for local development. This ensures developers can use familiar `invoke` commands with UV dependency management.

**Independent Test**: All invoke tasks (pytest, lint, black, mypy, isort, flake8, darglint, pre-commit, etc.) execute successfully using UV commands.

**Acceptance Scenarios**:

1. **Given** tasks.py uses `poetry run pytest`, **When** replaced with `uv run pytest`, **Then** invoke pytest command executes tests successfully
2. **Given** tasks.py uses `poetry run black`, **When** replaced with `uv run black`, **Then** invoke black command checks formatting correctly
3. **Given** tasks.py uses `poetry run mypy`, **When** replaced with `uv run mypy`, **Then** invoke mypy command performs type checking
4. **Given** tasks.py uses `poetry run pre-commit`, **When** replaced with `uv run pre-commit`, **Then** invoke pre-commit tasks work correctly

---

### User Story 5 - Documentation References UV (Priority: P5)

Update all documentation (README.md, CONTRIBUTING.md, AGENTS.md, docs/) to reference UV instead of Poetry for installation and development instructions.

**Why this priority**: Documentation changes are low-risk and high-impact. Updating documentation guides developers to use UV, completing the user-facing migration.

**Independent Test**: Documentation contains no Poetry installation or usage instructions for development, only UV commands are shown.

**Acceptance Scenarios**:

1. **Given** README.md has Poetry installation section, **When** updated to prioritize UV, **Then** UV is the recommended method, Poetry references are optional/deprecated
2. **Given** CONTRIBUTING.md references Poetry for setup, **When** updated to use UV, **Then** development setup instructions use UV commands
3. **Given** AGENTS.md lists Poetry in active technologies, **When** updated, **Then** UV replaces Poetry in the technology list
4. **Given** any documentation mentions `poetry run`, **When** updated, **Then** `uv run` is used instead

---

### Future User Stories

### User Story 6 - Cleanup Poetry References (Priority: P6)

Remove all Poetry-related files, configuration, and references that are no longer needed after migration is complete.

**Why this priority**: Cleanup removes technical debt and prevents confusion about which tool to use.

**Independent Test**: No Poetry files remain (pyproject.toml remains but Poetry-specific sections removed), no Poetry commands in any code or documentation.

**Acceptance Scenarios**:

1. **Given** completed migration stages 1-5, **When** removing Poetry files and references, **Then** no Poetry-related files or commands remain
2. **Given** pyproject.toml, **When** cleaned, **Then** Poetry-specific sections like [tool.poetry] are removed

---

### User Story 7 - Replace Nox with UV Scripts (Priority: P7)

Replace nox-based testing with UV-based scripts or tasks, eliminating the nox dependency entirely.

**Why this priority**: After full migration to UV, nox becomes redundant. Native UV scripts provide simpler, faster test execution.

**Independent Test**: All testing can be done without nox installed, using only UV and invoke.

**Acceptance Scenarios**:

1. **Given** noxfile.py with all sessions, **When** functionality moved to UV scripts or enhanced tasks.py, **Then** tests run without nox
2. **Given** UV-based test scripts, **When** invoked directly or through invoke, **Then** all test types (unit, integration, contract) pass

---

### Edge Cases

- What happens when Poetry is still installed alongside UV? (UV commands should take precedence)
- How does system handle Poetry references in git history? (Only current files need updating)
- What if a developer's local environment uses Poetry? (Migration should be backward compatible during transition)
- How does system handle uv.lock file conflicts? (Already migrated, no action needed)
- What happens with existing Poetry virtual environments? (Explicit cleanup commands provided in Stage 6)

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: GitHub workflows MUST use UV for package installation instead of Poetry
- **FR-002**: noxfile.py MUST use native nox with UV commands instead of nox-poetry
- **FR-003**: Source code MUST NOT invoke Poetry commands at runtime
- **FR-004**: tasks.py MUST use `uv run` instead of `poetry run` for all commands
- **FR-005**: Documentation MUST recommend UV as primary installation and development tool
- **FR-006**: Each migration stage MUST be independently testable with all tests passing
- **FR-007**: Migration stages must be functionally complete (tests pass) before proceeding to next stage; no ongoing Poetry compatibility required after Stage 5
- **FR-008**: All linting, testing, and build processes MUST work correctly after each stage

_GitHub Workflow Requirements:_

- **FR-009**: Tests workflow MUST install UV via pipx instead of Poetry
- **FR-010**: Tests workflow MUST install nox without nox-poetry plugin
- **FR-011**: Release workflow MUST use `uv build` instead of `poetry build`
- **FR-012**: Release workflow MUST use `uv run python -c ...` for version detection instead of `poetry version`

_Noxfile Requirements:_

- **FR-013**: noxfile.py MUST NOT import nox-poetry
- **FR-014**: Safety session MUST use `uv pip freeze` instead of `session.poetry.export_requirements()`
- **FR-015**: All session.install() calls MUST use `uv pip install` instead of Poetry dependency resolution

_Tasks.py Requirements:_

- **FR-016**: All `poetry run` commands MUST be replaced with `uv run`
- **FR-017**: Each invoke task MUST work correctly with UV commands

_Documentation Requirements:_

- **FR-018**: README.md MUST list UV as recommended installation method
- **FR-019**: CONTRIBUTING.md MUST use UV commands for setup instructions
- **FR-020**: AGENTS.md MUST list UV instead of Poetry in active technologies

### Key Entities

- **UV Package Manager**: Fast Python package installer and dependency manager replacing Poetry
- **uv.lock**: Lock file containing dependency information (already migrated from poetry.lock)
- **pyproject.toml**: Project configuration file (retained but Poetry-specific sections will be removed)
- **noxfile.py**: Nox session definitions file (updated to use UV instead of nox-poetry)
- **tasks.py**: Invoke task definitions file (updated to use uv run instead of poetry run)
- **GitHub Workflows**: CI/CD pipeline definitions (updated to install and use UV)

## Success Criteria _(mandatory)_

### Measurable Outcomes

> **Note on Performance**: Performance improvements (e.g., UV speed vs Poetry) are not formal requirements. Migration success is measured by functional correctness, not performance metrics.

- **SC-001**: GitHub Actions tests workflow passes all sessions on all platforms without Poetry installed
- **SC-002**: GitHub Actions release workflow successfully builds and publishes packages using UV
- **SC-003**: All nox sessions run successfully locally without nox-poetry installed
- **SC-004**: All invoke tasks execute successfully using UV commands
- **SC-005**: No Poetry commands remain in source code, tasks.py, or workflow files
- **SC-006**: Documentation references UV as primary tool, Poetry references removed or deprecated
- **SC-007**: Test coverage remains at 100% after migration
- **SC-008**: All pre-commit hooks pass using UV commands
- **SC-009**: Each of the 5 migration stages can be verified independently with tests passing

## Implementation Plan

### Stage 1: GitHub Workflows and Actions

**Files to modify**:
- `.github/workflows/tests.yml`
- `.github/workflows/release.yml`

**Changes required**:

#### `.github/workflows/tests.yml`:

1. Remove Poetry installation step:
   ```yaml
   # REMOVE these lines:
   - name: Install Poetry
     run: |
       pipx install --pip-args=--constraint=.github/workflows/constraints.txt poetry
       poetry self add poetry-plugin-export
       poetry --version
   ```

2. Add UV installation step:
   ```yaml
   # ADD:
   - name: Install UV
     run: |
       pipx install --pip-args=--constraint=.github/workflows/constraints.txt uv
       uv --version
   ```

3. Update Nox installation (remove nox-poetry):
   ```yaml
   # CHANGE from:
   - name: Install Nox
     run: |
       pipx install --pip-args=--constraint=.github/workflows/constraints.txt nox
       pipx inject --pip-args=--constraint=.github/workflows/constraints.txt nox nox-poetry
       nox --version

   # TO:
   - name: Install Nox
     run: |
       pipx install --pip-args=--constraint=.github/workflows/constraints.txt nox
       nox --version
   ```

4. Update coverage job tooling installation:
   ```yaml
   # CHANGE from:
   - name: Install tooling
     run: |
       pip install --constraint=.github/workflows/constraints.txt pip
       pipx install --pip-args=--constraint=.github/workflows/constraints.txt poetry
       pipx install --pip-args=--constraint=.github/workflows/constraints.txt nox
       pipx inject nox nox-poetry

   # TO:
   - name: Install tooling
     run: |
       pip install --constraint=.github/workflows/constraints.txt pip
       pipx install --pip-args=--constraint=.github/workflows/constraints.txt uv
       pipx install --pip-args=--constraint=.github/workflows/constraints.txt nox
   ```

#### `.github/workflows/release.yml`:

1. Replace Poetry installation with UV:
   ```yaml
   # CHANGE from:
   - name: Install Poetry
     run: |
       pipx install --pip-args=--constraint=.github/workflows/constraints.txt poetry
       poetry --version

   # TO:
   - name: Install UV
     run: |
       pipx install --pip-args=--constraint=.github/workflows/constraints.txt uv
       uv --version
   ```

2. Replace version detection commands:
    ```yaml
    # CHANGE from:
    version-command: |
      bash -o pipefail -c "poetry version | awk '{ print \$2 }'"

    # TO:
    version-command: |
      bash -o pipefail -c "uv run python -c \"import tomli; print(tomli.load(open('pyproject.toml'))['project']['version'])\""
    ```

3. Replace version bump for developmental release:
   ```yaml
   # CHANGE from:
   - name: Bump version for developmental release
     if: "! steps.check-version.outputs.tag"
     run: |
       poetry version patch &&
       version=$(poetry version | awk '{ print $2 }') &&
       poetry version $version.dev.$(date +%s)

   # TO:
   - name: Bump version for developmental release
     if: "! steps.check-version.outputs.tag"
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
   ```

4. Replace build command:
   ```yaml
   # CHANGE from:
   - name: Build package
     run: |
       poetry build --ansi

   # TO:
   - name: Build package
     run: |
       uv build
   ```

**Testing after Stage 1**:
- Create test branch
- Apply workflow changes
- Push to trigger GitHub Actions
- Verify tests.yml passes on all platforms (ubuntu, windows, macos)
- Verify release.yml builds package correctly
- Confirm coverage upload and report generation work

**Expected outcomes**:
- All CI/CD tests pass without Poetry
- Build artifacts generated successfully
- Coverage reports created and uploaded

---

### Stage 2: noxfile.py (keep nox, replace poetry with uv)

**Files to modify**:
- `noxfile.py`
- `pyproject.toml` (remove nox-poetry from dev dependencies)

**Changes required**:

#### `noxfile.py`:

1. Remove nox-poetry imports and error handling:
   ```python
   # REMOVE:
   try:
       from nox_poetry import Session
       from nox_poetry import session
   except ImportError:
       message = f"""\
       Nox failed to import the 'nox-poetry' package.

       Please install it using the following command:

       {sys.executable} -m pip install nox-poetry"""
       raise SystemExit(dedent(message)) from None

   # REPLACE with:
   from nox import Session
   from nox import session
   ```

2. Update all session.install() calls to use uv pip install pattern:
   ```python
   # CHANGE pattern from:
   session.install("package", "another-package")

   # TO (for most cases, direct install still works):
   session.install("package", "another-package")

   # BUT for the package itself, use uv:
   session.install(".")
   ```

3. Update safety session to use uv pip freeze:
   ```python
   # CHANGE from:
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

   # TO:
   @session(python=python_versions)
   def safety(session: Session) -> None:
       """Scan dependencies for insecure packages."""
       # Export requirements using uv
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

4. Update all sessions to install with uv:
   ```python
   # For all sessions that need package installation:
   session.install(".")  # This installs the current package
   # Nox will use pip in the nox venv, which is fine

   # Optionally, to use uv for installs:
   session.run("uv", "pip", "install", ".", external=True)
   session.run("uv", "pip", "install", "pytest", "coverage", external=True)
   ```

5. Remove activate_virtualenv_in_precommit_hooks function if no longer needed (can be kept as it works with nox's virtualenv management)

#### `pyproject.toml`:

1. Remove nox-poetry from dev dependencies:
   ```toml
   # CHANGE from:
   [dependency-groups]
   dev = [
       ...
       "nox>=2025.11.12,<2026",
       "nox-poetry>=1.2.0,<2",
   ]

   # TO:
   [dependency-groups]
   dev = [
       ...
       "nox>=2025.11.12,<2026",
   ]
   ```

**Testing after Stage 2**:
- Apply noxfile.py changes
- Update pyproject.toml dependencies
- Run `nox --list-sessions` to verify sessions are available
- Run `nox -s tests` to verify test suite works
- Run `nox -s mypy` to verify type checking works
- Run `nox -s pre-commit` to verify pre-commit hooks work
- Run `nox -s docs-build` to verify docs build works
- Run all sessions to ensure complete functionality

**Expected outcomes**:
- All nox sessions execute without nox-poetry
- Tests, linting, type checking, and docs build all work
- No Poetry dependencies in development environment

---

### Stage 3: Source Code (actual source code)

**Files to check**:
- All files in `src/ord_plan/` directory
- Check for any subprocess calls to Poetry
- Check for any Poetry-specific imports or logic

**Changes required**:

1. Search for Poetry references:
   ```bash
   grep -r "poetry" src/
   ```

2. If any Poetry commands found in source code, replace with UV equivalents:
   ```python
   # CHANGE from:
   subprocess.run(["poetry", "run", "command"], ...)

   # TO:
   subprocess.run(["uv", "run", "command"], ...)
   ```

3. If any Poetry-specific imports:
   ```python
   # REMOVE if found:
   # from poetry.core... (unlikely to exist but check)
   ```

**Testing after Stage 3**:
- Search for remaining Poetry references in source code
- Run full test suite: `invoke pytest` or `nox -s tests`
- Verify all source code executes without Poetry dependency
- Import main module and verify no Poetry errors

**Expected outcomes**:
- No Poetry commands or imports in source code
- All tests pass without Poetry
- Code executes correctly using UV for any subprocess calls

---

### Stage 4: tasks.py

**Files to modify**:
- `tasks.py`

**Changes required**:

Replace all `poetry run` commands with `uv run`:

```python
# CHANGE from:
@task
def pytest(c):
    """Run pytest tests."""
    setup_python_path()
    return run_command(
        c,
        (
            "poetry run pytest tests/ -v --cov=ord_plan --cov-report=term-missing "
            "-W ignore::DeprecationWarning"
        ),
        "Running pytest tests",
    )

# TO:
@task
def pytest(c):
    """Run pytest tests."""
    setup_python_path()
    return run_command(
        c,
        (
            "uv run pytest tests/ -v --cov=ord_plan --cov-report=term-missing "
            "-W ignore::DeprecationWarning"
        ),
        "Running pytest tests",
    )
```

Continue for all tasks:

1. **test_unit**:
   ```python
   # CHANGE: "poetry run pytest tests/unit/ -v"
   # TO: "uv run pytest tests/unit/ -v"
   ```

2. **test_integration**:
   ```python
   # CHANGE: "poetry run pytest tests/integration/ -v"
   # TO: "uv run pytest tests/integration/ -v"
   ```

3. **test_contract**:
   ```python
   # CHANGE: "poetry run pytest tests/contract/ -v"
   # TO: "uv run pytest tests/contract/ -v"
   ```

4. **pre_commit**:
   ```python
   # CHANGE: "poetry run pre-commit run --all-files"
   # TO: "uv run pre-commit run --all-files"
   ```

5. **pre_commit_install**:
   ```python
   # CHANGE: "poetry run pre-commit install"
   # TO: "uv run pre-commit install"
   ```

6. **security**:
   ```python
   # CHANGE: "poetry run safety check"
   # TO: "uv run safety check"
   ```

7. **mypy**:
   ```python
   # CHANGE: "poetry run mypy src/ --ignore-missing-imports"
   # TO: "uv run mypy src/ --ignore-missing-imports"
   ```

8. **black**:
   ```python
   # CHANGE: "poetry run black --check src/ tests/"
   # TO: "uv run black --check src/ tests/"
   ```

9. **isort**:
   ```python
   # CHANGE: "poetry run isort --check-only src/ tests/"
   # TO: "uv run isort --check-only src/ tests/"
   ```

10. **flake8**:
    ```python
    # CHANGE: "poetry run flake8 src/ tests/"
    # TO: "uv run flake8 src/ tests/"
    ```

11. **darglint**:
    ```python
    # CHANGE: 'poetry run darglint --ignore-raise "FileNotFoundError,PermissionError,OSError,BadParameter" src/'
    # TO: 'uv run darglint --ignore-raise "FileNotFoundError,PermissionError,OSError,BadParameter" src/'
    ```

**Testing after Stage 4**:
- Apply all changes to tasks.py
- Run `invoke pytest` - should work
- Run `invoke test-unit` - should work
- Run `invoke test-integration` - should work
- Run `invoke lint` - should work (includes black, isort, flake8, mypy, darglint)
- Run `invoke pre-commit` - should work
- Run `invoke all` - should run all checks successfully
- Run `invoke help` - verify help output is still correct

**Expected outcomes**:
- All invoke tasks execute with UV commands
- All tests pass
- All linting checks pass
- Development workflow unchanged from user perspective (same invoke commands)

---

### Stage 5: Documentation, README, anywhere else

**Files to modify**:
- `README.md`
- `CONTRIBUTING.md`
- `AGENTS.md`
- `.pre-commit-config.yaml`
- `Dockerfile`

**Changes required**:

#### `README.md`:

1. Update Installation section - prioritize UV:
   ```markdown
   # CHANGE from:
   ### Method 1: uv (Recommended)

   [uv](https://docs.astral.sh/uv/) is modern, fast Python package installer:

   ```console
   # Install as a system tool (recommended for most users)
   $ uv tool install ord-plan
   ```

   ### Method 2: Poetry

   If you're using [Poetry](https://python-poetry.org/) for dependency management:

   ```console
   # Add to your project
   $ poetry add ord-plan

   # Or install globally
   $ poetry global add ord-plan
   ```

   # TO:
   ### Method 1: uv (Recommended)

   [uv](https://docs.astral.sh/uv/) is modern, fast Python package installer:

   ```console
   # Install as a system tool (recommended for most users)
   $ uv tool install ord-plan
   ```

   ### Method 2: pip

   Traditional installation using pip:
   ```

   Remove Poetry installation section entirely or move to deprecated methods section.

2. Update Development Installation section:
   ```markdown
   # CHANGE from:
   #### Using uv

   ```console
   # Clone repository
   $ git clone https://github.com/vonpupp/ord-plan.git
   $ cd ord-plan

   # Install in editable mode for development
   $ uv pip install -e .
   ```

   #### Using Poetry

   ```console
   # Clone the repository
   $ git clone https://github.com/vonpupp/ord-plan.git
   $ cd ord-plan

   # Install in editable mode
   $ poetry install
   $ poetry shell  # Activate the virtual environment
   ```

   # TO:
   #### Using uv

   ```console
   # Clone repository
   $ git clone https://github.com/vonpupp/ord-plan.git
   $ cd ord-plan

   # Install in editable mode for development
   $ uv pip install -e .
   ```

   Remove Poetry section.
   ```

3. Update Pre-commit Hooks section:
   ```markdown
   # CHANGE from:
   Or run directly with poetry:

   ```bash
   poetry run pre-commit run --all-files
   ```

   # TO:
   Or run directly with uv:

   ```bash
   uv run pre-commit run --all-files
   ```

   Pre-commit hooks are configured in `.pre-commit-config.yaml` and use uv to ensure all tools run in the correct virtual environment.
   ```

4. Remove Poetry link from footer:
   ```markdown
   # CHANGE from:
   [poetry]: https://python-poetry.org/
   [uv]: https://docs.astral.sh/uv/

   # TO:
   [uv]: https://docs.astral.sh/uv/
   ```

5. Update development environment setup:
   ```markdown
   # CHANGE from:
   Using Poetry:

   ```bash
   poetry install
   ```

   # TO:
   Using uv:

   ```bash
   uv pip install -e ".[dev]"
   ```
   ```

#### `CONTRIBUTING.md`:

1. Update How to set up your development environment section:
   ```markdown
   # CHANGE from:
   You need Python 3.7+ and the following tools:

   - [Poetry]
   - [Nox]
   - [nox-poetry]

   Install the package with development requirements:

   ```console
   $ poetry install
   ```

   You can now run an interactive Python session,
   or the command-line interface:

   ```console
   $ poetry run python
   $ poetry run ord-plan
   ```

   [poetry]: https://python-poetry.org/
   [nox]: https://nox.thea.codes/
   [nox-poetry]: https://nox-poetry.readthedocs.io/

   # TO:
   You need Python 3.7+ and the following tools:

   - [uv]
   - [Nox]

   Install the package with development requirements:

   ```console
   $ uv pip install -e ".[dev]"
   ```

   You can now run an interactive Python session,
   or the command-line interface:

   ```console
   $ uv run python
   $ uv run ord-plan
   ```

   [uv]: https://docs.astral.sh/uv/
   [nox]: https://nox.thea.codes/
   ```

2. Remove duplicate Nox sessions list section (appears twice)

#### `AGENTS.md`:

1. Update Active Technologies section:
   ```markdown
   # CHANGE from:
   ## Active Technologies
   - Python 3.7+ (as specified in pyproject.toml) + Click (>=8.0.1), PyYAML, Poetry for dependency management (004-add-format-flag)
   - Files (YAML configuration and org-mode output) (004-add-format-flag)

   - Python 3.7+ (as specified in pyproject.toml) + Click (>=8.0.1), Poetry for dependency management (001-generate-org)

   # TO:
   ## Active Technologies
   - Python 3.7+ (as specified in pyproject.toml) + Click (>=8.0.1), PyYAML, UV for dependency management (004-add-format-flag)
   - Files (YAML configuration and org-mode output) (004-add-format-flag)

   - Python 3.7+ (as specified in pyproject.toml) + Click (>=8.0.1), UV for dependency management (001-generate-org)
   ```

2. Update Pre-commit Hooks section:
   ```markdown
   # CHANGE from:
   Or run directly with poetry:

   ```bash
   poetry run pre-commit run --all-files
   ```

   Pre-commit hooks are configured in `.pre-commit-config.yaml` and use poetry to ensure all tools run in the correct virtual environment.

   # TO:
   Or run directly with uv:

   ```bash
   uv run pre-commit run --all-files
   ```

   Pre-commit hooks are configured in `.pre-commit-config.yaml` and use uv to ensure all tools run in the correct virtual environment.
   ```

3. Update Recent Changes section:
   ```markdown
   # CHANGE from:
   - 004-add-format-flag: Added Python 3.7+ (as specified in pyproject.toml) + Click (>=8.0.1), PyYAML, Poetry for dependency management

   - 001-generate-org: Added Python 3.7+ (as specified in pyproject.toml) + Click (>=8.0.1), Poetry for dependency management

   # TO:
   - 004-add-format-flag: Added Python 3.7+ (as specified in pyproject.toml) + Click (>=8.0.1), PyYAML, UV for dependency management

   - 001-generate-org: Added Python 3.7+ (as specified in pyproject.toml) + Click (>=8.0.1), UV for dependency management

   - 005-migrate-poetry-to-uv: Migrated from Poetry to UV for dependency management
   ```

#### `.pre-commit-config.yaml`:

Replace all `poetry run` with `uv run`:

```yaml
# CHANGE all entries from:
- id: black
  name: black
  entry: poetry run black
  language: system

# TO:
- id: black
  name: black
  entry: uv run black
  language: system
```

Repeat for all hooks:
- black
- check-added-large-files
- check-toml
- check-yaml
- darglint
- end-of-file-fixer
- flake8
- isort
- pyupgrade
- trailing-whitespace

#### `Dockerfile`:

Update to use UV instead of Poetry:

```dockerfile
# CHANGE from:
# Install pipx (required for Poetry and Nox)
RUN python -m pip install --user pipx
RUN python -m pipx ensurepath

ENV PATH="/root/.local/bin:$PATH"

# Install tools with constraints (mimic GitHub Actions exactly)
WORKDIR /workspace
COPY .github/workflows/constraints.txt /tmp/constraints.txt
RUN pipx install --pip-args=--constraint=/tmp/constraints.txt poetry
RUN pipx install --pip-args=--constraint=/tmp/constraints.txt nox
RUN pipx inject --pip-args=--constraint=/tmp/constraints.txt nox nox-poetry

# Verify installations
RUN poetry --version
RUN poetry config installer.parallel false || true
RUN poetry self add poetry-plugin-export
RUN nox --version

# TO:
# Install pipx (required for UV and Nox)
RUN python -m pip install --user pipx
RUN python -m pipx ensurepath

ENV PATH="/root/.local/bin:$PATH"

# Install tools with constraints (mimic GitHub Actions exactly)
WORKDIR /workspace
COPY .github/workflows/constraints.txt /tmp/constraints.txt
RUN pipx install --pip-args=--constraint=/tmp/constraints.txt uv
RUN pipx install --pip-args=--constraint=/tmp/constraints.txt nox

# Verify installations
RUN uv --version
RUN nox --version
```

**Testing after Stage 5**:
- Update all documentation files
- Run `grep -r "poetry" .` to verify only git history or comments remain
- Build documentation: `invoke docs`
- Run all tests: `invoke all`
- Verify Dockerfile builds correctly
- Read through all documentation to ensure consistency

**Expected outcomes**:
- No Poetry references in documentation
- UV is documented as primary tool
- All documentation is accurate and up-to-date
- Pre-commit hooks work with UV
- Docker image builds and runs tests correctly

---

### Future Stage 6: Cleanup (remove all poetry references)

**Files to modify**:
- `pyproject.toml` (remove Poetry-specific sections if present)
- Remove any Poetry configuration files (pyproject.toml's [tool.poetry] section)

**Changes required**:

1. Check pyproject.toml for Poetry-specific sections:
   ```toml
   # REMOVE if present:
   [tool.poetry]
   name = "ord-plan"
   version = "..."
   ...

   [tool.poetry.dependencies]
   ...

   [tool.poetry.dev-dependencies]
   ...

   [build-system]
   requires = ["poetry-core"]
   build-backend = "poetry.core.masonry.api"
   ```

2. Ensure pyproject.toml uses [project] section (already the case):
   ```toml
   [project]
   name = "ord-plan"
   version = "0.0.1"
   ...
   ```

3. Search for any remaining Poetry references:
    ```bash
    grep -r "poetry" . --exclude-dir=.git --exclude-dir=__pycache__
    ```

4. Provide cleanup commands for Poetry virtual environments:
    ```bash
    # Find and remove Poetry virtual environments
    # Poetry venvs are typically in ~/.local/share/pypoetry/venvs/
    poetry env list --full-path  # List all Poetry virtual environments
    poetry env remove --all  # Remove all Poetry virtual environments

    # Alternatively, manually remove Poetry cache and venvs:
    rm -rf ~/.cache/pypoetry/
    rm -rf ~/.local/share/pypoetry/venvs/

    # Optionally uninstall Poetry itself after confirming migration successful:
    pipx uninstall poetry
    ```

**Testing after Stage 6**:
- Verify no Poetry files remain (no pyproject.toml poetry sections)
- Verify no Poetry commands in any files
- Run all tests to ensure nothing broken
- Check for any Poetry-specific configuration files

**Expected outcomes**:
- No Poetry-specific configuration remains
- All references to Poetry removed
- Project fully migrated to UV

---

### Future Stage 7: Replace Nox with UV Scripts

**Files to create/modify**:
- Create new test scripts using UV
- Optionally modify `tasks.py` to replace nox functionality
- Optionally remove `noxfile.py`

**Changes required**:

1. Option 1: Keep nox but use UV for all operations (simpler transition)

2. Option 2: Replace nox with UV-based scripts:
   - Create scripts/ directory with test scripts
   - Use `uv run pytest` directly
   - Use `uv run mypy` directly
   - Use `uv run pre-commit` directly

3. Enhance tasks.py to cover all nox sessions:
   ```python
   @task
   def pytest(c, coverage=False):
       """Run pytest tests."""
       setup_python_path()
       cmd = "uv run pytest tests/"
       if coverage:
           cmd += " -v --cov=ord_plan --cov-report=term-missing"
       return run_command(c, cmd, "Running pytest tests")

   @task
   def docs_build(c):
       """Build documentation."""
       setup_python_path()
       return run_command(c, "uv run sphinx-build docs docs/_build", "Building docs")
   ```

**Testing after Stage 7**:
- Run all tests without nox
- Verify all test types work (unit, integration, contract)
- Verify linting works
- Verify docs build
- Optionally: Remove noxfile.py and verify nothing broken

**Expected outcomes**:
- All testing works without nox
- Simpler dependency management (only UV needed)
- Faster test execution (UV is faster than nox+poetry)

---

## Rollback Plan

**Failure Strategy**: If any migration stage fails (tests do not pass), the entire migration should be halted. Each stage must succeed before proceeding to the next stage.

If a stage fails, rollback steps:

1. **Stage 1**: Restore workflow files from git
2. **Stage 2**: Restore noxfile.py and pyproject.toml from git, reinstall nox-poetry
3. **Stage 3**: Revert any source code changes
4. **Stage 4**: Restore tasks.py from git
5. **Stage 5**: Restore documentation from git

Restart migration from Stage 1 after rollback.

## Testing Strategy

### Per-Stage Verification

Each stage must be verified independently:

1. **Stage 1**: Push changes, verify GitHub Actions pass
2. **Stage 2**: Run all nox sessions locally
3. **Stage 3**: Run full test suite
4. **Stage 4**: Run all invoke tasks
5. **Stage 5**: Verify documentation accuracy, run pre-commit hooks

### Final Integration Testing

After all 5 stages complete:

1. Run `invoke all` - all checks must pass
2. Run `nox` - all sessions must pass
3. Create PR, verify CI/CD passes
4. Build documentation, verify accuracy
5. Test Docker build

### Acceptance Testing

1. Developer can clone repo, run `uv pip install -e ".[dev]"`
2. Developer can run `invoke pytest` successfully
3. Developer can run `invoke lint` successfully
4. No Poetry installation required anywhere
5. All documentation references UV

## Dependencies

- UV must be available (pipx install uv)
- Python 3.9+ (current requirement)
- Existing test infrastructure must remain functional
