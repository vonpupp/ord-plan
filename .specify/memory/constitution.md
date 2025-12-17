<!-- Sync Impact Report:
- Version change: 1.0.0 → 1.1.0 (template consistency update + CLI-specific requirements)
- Modified principles: None (principles unchanged, but enhanced with implementation details)
- Added sections: CLI-specific functional requirements in spec template, detailed project structure in plan template
- Removed sections: None
- Templates requiring updates: ✅ plan-template.md, ✅ spec-template.md, ✅ tasks-template.md
- Follow-up TODOs: None
-->

# ORD Plan Constitution

## Core Principles

### I. CLI-First Design
Every feature must be accessible via command-line interface. Text-based I/O protocol: stdin/args → stdout, errors → stderr. Support both org-mode (primary) and JSON (secondary) output formats. CLI commands must be self-documenting and follow POSIX conventions.

### II. Test-Driven Development (NON-NEGOTIABLE)
TDD mandatory: Write failing tests → Get user approval → Implement code → Refactor. Red-Green-Refactor cycle strictly enforced. All tests must pass before any commit. 100% test pass is required for all new code paths.

### III. Org-Mode Native
Org-mode is the primary output format. All data structures MUST map cleanly to org-mode syntax (headlines, properties, tables, timestamps). When generating org-mode content, validate output against org-mode parser standards. JSON output is secondary and must serialize from the same data model.

### IV. Template Generation Focus
Core functionality is generating structured data templates. Templates must be reproducible, configurable, and validate against org-mode schema requirements. Template customization uses configuration files, not code modifications.

### V. Hypermodern Python Standards
Follow all hypermodern Python cookiecutter conventions: Poetry for dependency management, Black for formatting, mypy for type checking, pre-commit hooks, pytest for testing, comprehensive documentation, and semantic versioning.

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
- **Tests**: pytest with coverage >= 50%, no skipping tests
- **Types**: mypy strict mode, no any types allowed
- **Docs**: sphinx build successful, coverage of new features
- **Integration**: CLI commands tested end-to-end

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

**Version**: 1.1.1 | **Ratified**: 2025-12-16 | **Last Amended**: 2025-12-16
