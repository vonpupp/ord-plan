<!-- Sync Impact Report:
- Version change: 1.2.0 → 1.3.0 (migrated from bin/test.sh to invoke task automation)
- Modified principles: Comprehensive Testing Requirements (updated testing interface from bin/test.sh to invoke)
- Added sections: Invoke task mappings, individual test task support, help task
- Removed sections: bin/test.sh references
- Templates requiring updates: ✅ plan-template.md, ✅ spec-template.md, ✅ tasks-template.md
- Follow-up TODOs: None
-->

# ORD Plan Constitution

## Core Principles

### I. CLI-First Design

Every feature must be accessible via command-line interface. Text-based I/O protocol: stdin/args → stdout, errors → stderr. Support both org-mode (primary) and JSON (secondary) output formats. CLI commands must be self-documenting and follow POSIX conventions.

### II. Test-Driven Development (NON-NEGOTIABLE)

TDD mandatory: Write failing tests → Get user approval → Implement code → Refactor. Red-Green-Refactor cycle strictly enforced. All tests must pass before any commit. 100% test pass is required for all new code paths.

#### Testing Patterns and Fixtures

All test data MUST be centralized in `tests/fixtures/` directory. No inline test data or scattered test files allowed. Use dedicated helper functions in `tests/fixtures.py` for fixture access:

- `get_fixture_path(filename)` - Get absolute path to fixture
- `read_fixture(filename)` - Read fixture contents as string
- `write_to_fixture(filename, content)` - Write temporary fixtures
- `list_fixtures()` - List all available fixtures

Fixture naming convention: `test_{purpose}_{scenario}.{ext}` (e.g., `test_rules_basic.yaml`, `existing_content.org`).

### III. Org-Mode Native

Org-mode is the primary output format. All data structures MUST map cleanly to org-mode syntax (headlines, properties, tables, timestamps). When generating org-mode content, validate output against org-mode parser standards. JSON output is secondary and must serialize from the same data model.

### IV. Template Generation Focus

Core functionality is generating structured data templates. Templates must be reproducible, configurable, and validate against org-mode schema requirements. Template customization uses configuration files, not code modifications.

### V. Hypermodern Python Standards

Follow all hypermodern Python cookiecutter conventions: Poetry for dependency management, Black for formatting, mypy for type checking, pre-commit hooks, pytest for testing, comprehensive documentation, and semantic versioning.

### VI. No Performance Testing

Performance testing and optimization is explicitly out of scope. Focus on correct functionality and maintainability rather than performance benchmarks. No performance-related test files, metrics, or optimization efforts should be included in the codebase.

## Technical Standards

### Technology Stack

- **Language**: Python 3.7+ (as specified in pyproject.toml)
- **CLI Framework**: Click (>=8.0.1)
- **Testing**: pytest with coverage >= 50%
- **Type Checking**: mypy in strict mode
- **Documentation**: Sphinx with Read the Docs deployment
- **Code Quality**: Black, isort, flake8 with comprehensive plugins

### Security Standards

- No external network calls by default
- Configuration files must be validated before processing
- Generated templates must be safe from injection attacks
- User input sanitization mandatory

## Development Workflow

### Code Review Process

All changes require pull request review with:

- Compliance check against all constitution principles
- Automated test suite passing (100% pass)
- Type checking with mypy
- Code formatting with Black and isort
- Security scan with bandit
- Documentation updates if API changes

### Quality Gates

- **Pre-commit**: All hooks must pass (formatting, linting, security)
- **Tests**: pytest with coverage >= 50%, no skipping tests, all fixtures centralized
- **Types**: mypy strict mode, no any types allowed
- **Docs**: sphinx build successful, coverage of new features
- **Integration**: CLI commands tested end-to-end

### Comprehensive Testing Requirements

All testing and code quality checks MUST be run through the single entry point: `invoke`. This is the ONLY authorized way to run tests for the project. Individual invoke tasks are available for specific testing needs, but full workflow compliance requires using appropriate invoke commands.

**Required Test Components (available through invoke tasks):**

- **Type Checking**: `invoke mypy` - mypy strict mode with all error codes enabled
- **Code Style**: `invoke flake8` - ruff or flake8 linting with automatic fixing where possible
- **Coverage Analysis**: `invoke pytest` - pytest-cov with minimum 50% coverage requirement
- **Linting**: `invoke lint` - All linting checks (black, isort, flake8, mypy, darglint)

**Usage Requirements:**

- ALL development must use `invoke` commands for validation
- Individual tasks (`invoke pytest`, `invoke mypy`, etc.) are allowed for targeted testing
- Pre-commit hooks must call `invoke lint mypy pytest` or `invoke all`
- Pull request validation requires `invoke all` to pass
- Documentation must reference `invoke` as the primary testing interface
- Use `invoke help` for comprehensive usage guidance

### File Management Rules

**NO TEST FILES IN PROJECT ROOT**: Test and debug files MUST be created only in `tests/fixtures/` directory or `tmp/` directories. Never create test files in the project root directory. Any test files outside designated locations must be immediately removed.

- **Fixtures Location**: All test data belongs in `tests/fixtures/` using proper naming conventions
- **Temporary Files**: Quick tests may use `/tmp/` or project's temporary directories
- **Clean Up Required**: Any test/debug files created during development must be removed before commits
- **Exception**: Files in `tests/fixtures/` are version-controlled and intended for testing

### Release Process

- Semantic versioning (MAJOR.MINOR.PATCH)
- Changelog entries required for all changes
- Release candidates tested on multiple Python versions
- Documentation updated and deployed before PyPI release

## Governance

This constitution supersedes all other development practices and guidelines. Amendments require:

- Written proposal with impact analysis
- Team review and approval
- Version bump according to semantic versioning rules
- Migration plan for affected code and documentation
- Update of all template files and guidance documents

All pull requests and code reviews must verify compliance with constitution principles. Any complexity or deviation from these principles must be explicitly justified with alternatives considered and rejected.

**Version**: 1.3.1 | **Ratified**: 2025-12-16 | **Last Amended**: 2025-12-18
