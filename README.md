# ORD Plan

[![PyPI](https://img.shields.io/pypi/v/ord-plan.svg)][pypi_]
[![Status](https://img.shields.io/pypi/status/ord-plan.svg)][status]
[![Python Version](https://img.shields.io/pypi/pyversions/ord-plan)][python version]
[![License](https://img.shields.io/pypi/l/ord-plan)][license]

[![Read the documentation at https://ord-plan.readthedocs.io/](https://img.shields.io/readthedocs/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/vonpupp/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/vonpupp/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

ORD Plan is a powerful CLI tool for generating structured org-mode events from cron-based YAML rules. It helps you create automated task schedules while preserving existing content in your org files.

[pypi_]: https://pypi.org/project/
[status]: https://pypi.org/project/
[python version]: https://pypi.org/project/ord-plan
[read the docs]: https://ord-plan.readthedocs.io/
[tests]: https://github.com/vonpupp/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/vonpupp/ord-plan
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## ✨ Features

- 🚀 **Fast CLI** - Generate thousands of events in seconds
- 📅 **Flexible Scheduling** - Full cron expression support
- 📝 **Org-mode Native** - Perfect integration with Emacs org-mode
- 🔄 **Content Preservation** - Safely merge with existing org files
- ⚡ **Performance Optimized** - Efficient processing of large date ranges
- 🛡️ **Date Protection** - Warnings for potentially dangerous date ranges
- 🎯 **Dry Run Mode** - Preview changes before applying them
- 🌍 **Unicode Support** - Full international character support
- 🔧 **Configurable** - Custom date formats and behavior

## 📋 Requirements

- Python 3.7+
- Click 8.0.1+

## 🚀 Installation

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

### Method 3: pip

Traditional installation using pip:

```console
# Install from PyPI
$ pip install ord-plan

# Or install with user permissions only
$ pip install --user ord-plan
```

### Development Installation (Editable)

For contributors who want to modify the code:

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

#### Using pip

```console
# Clone the repository
$ git clone https://github.com/vonpupp/ord-plan.git
$ cd ord-plan

# Create and activate virtual environment (optional but recommended)
$ python -m venv venv
$ source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode
$ pip install -e .
```

## 🎯 Quick Start

### 1. Create a Rules File

Create `my-rules.yaml` with your recurring events:

```yaml
REVERSE_DATETREE_WEEK_FORMAT: "%Y-W%V"
REVERSE_DATETREE_DATE_FORMAT: "%Y-%m-%d %a"
REVERSE_DATETREE_YEAR_FORMAT: "%Y"

events:
  - title: "Morning Exercise"
    cron: "0 7 * * 1,3,5"
    tags: ["health", "exercise"]
    description: "Daily morning workout routine"
  - title: "Team Meeting"
    cron: "0 14 * * 2"
    todo_state: "TODO"
    tags: ["work", "meeting"]
    description: |
      Weekly team sync meeting
      - [ ] Review agenda
      - [ ] Prepare updates
      - [ ] Assign action items
  - title: "Code Review"
    cron: "0 16 * * 4"
    tags: ["work", "development"]
    description: "Review pull requests and code changes"
```

### 2. Generate Events

```bash
# Generate for this week (default behavior)
ord-plan generate --rules my-rules.yaml --file tasks.org

# Generate for specific date range
ord-plan generate --rules my-rules.yaml --from 2025-01-01 --to 2025-01-31 --file january.org

# Preview output before saving
ord-plan generate --rules my-rules.yaml --from today --to "+7 days"
```

### 3. Generated Output

The tool creates structured org-mode content like this:

```org
* 2025
** 2025-W03
*** 2025-01-20 Mon
**** Morning Exercise                     :health:exercise:
Daily morning workout routine
**** TODO Team Meeting                       :work:meeting:
Weekly team sync meeting
- [ ] Review agenda
- [ ] Prepare updates
- [ ] Assign action items
*** 2025-01-22 Wed
**** Morning Exercise                     :health:exercise:
Daily morning workout routine
*** 2025-01-23 Thu
**** Code Review                         :work:development:
Review pull requests and code changes
```

## 📚 Command Reference

### `ord-plan generate`

Generate org-mode events from cron-based rules.

#### Options

| Option         | Required | Description                                                       |
| -------------- | -------- | ----------------------------------------------------------------- |
| `--rules PATH` | Yes      | Path to YAML rules file containing event definitions              |
| `--file PATH`  | No       | Path to target org-mode file (default: stdout)                    |
| `--from DATE`  | No       | Start date for event generation (default: Monday of current week) |
| `--to DATE`    | No       | End date for event generation (default: Sunday of current week)   |
| `--force`      | No       | Bypass past/future date warnings (use with caution)               |
| `--dry-run`    | No       | Show what would be generated without creating files               |

#### Date Formats

- **Absolute**: `YYYY-MM-DD` (e.g., `2025-01-15`)
- **Relative**: `today`, `tomorrow`, `yesterday`, `next monday`, `next week`, `next month`, `next year`
- **Offset**: `+N days` (e.g., `+7 days` for one week from now)

### Examples

#### Generate Events for Current Week

```bash
ord-plan generate --rules my-events.yaml --file weekly-tasks.org
```

#### Custom Date Range

```bash
# Generate for January 2025
ord-plan generate --rules events.yaml --from 2025-01-01 --to 2025-01-31 --file january.org

# Generate for next 30 days
ord-plan generate --rules events.yaml --from today --to "+30 days" --file upcoming.org

# Generate for next month
ord-plan generate --rules events.yaml --from next month --to "+30 days" --file february.org
```

#### Working with Existing Files

```bash
# Add events to existing org file (preserves current content)
ord-plan generate --rules work-events.yaml --file existing-work.org

# Check what would be added without modifying file
ord-plan generate --rules work-events.yaml --file existing-work.org --dry-run
```

For complete documentation, see the [Command-line Reference](https://ord-plan.readthedocs.io/en/latest/usage.html).

## 🔧 Configuration

### Environment Variables

```bash
export ORD_PLAN_YEAR_FORMAT="%Y"
export ORD_PLAN_WEEK_FORMAT="%Y Week %W"
export ORD_PLAN_DATE_FORMAT="%B %d, %Y"
export ORD_PLAN_DEFAULT_TODO_STATE="TODO"
export ORD_PLAN_MAX_EVENTS="5000"
export ORD_PLAN_TIMEOUT="60"
```

### YAML Configuration File

```yaml
# Custom date formats
REVERSE_DATETREE_YEAR_FORMAT: "%Y"
REVERSE_DATETREE_WEEK_FORMAT: "Week %W, %Y"
REVERSE_DATETREE_DATE_FORMAT: "%A, %B %d, %Y"

# Performance limits
max_events_per_file: 5000
processing_timeout_seconds: 60

events:
  - title: "Custom Formatted Event"
    cron: "0 9 * * 1"
```

## ⚙️ Cron Expression Examples

| Schedule                | Cron Expression  | Description                        |
| ----------------------- | ---------------- | ---------------------------------- |
| Daily at 9 AM           | `0 9 * * *`      | Every day at 9:00 AM               |
| Weekdays at 2 PM        | `0 14 * * 1-5`   | Monday-Friday at 2:00 PM           |
| Monday/Wednesday/Friday | `0 0 * * 1,3,5`  | Mon, Wed, Fri at midnight          |
| First of month          | `0 0 1 * *`      | 1st day of each month              |
| Every 2 hours           | `0 */2 * * *`    | Every 2 hours on the hour          |
| Work days 9-5           | `0 9-17 * * 1-5` | Hourly from 9 AM to 5 PM, weekdays |

> **Note**: Cron format is `minute hour day month weekday` where weekday is 0=Sunday, 6=Saturday.

## 🏗️ Development

### Setting Up Development Environment

1. **Clone the repository**:

   ```bash
   git clone https://github.com/vonpupp/ord-plan.git
   cd ord-plan
   ```

2. **Install development dependencies**:

   Using uv:

   ```bash
   uv pip install -e ".[dev]"
   ```

   Using Poetry:

   ```bash
   poetry install
   ```

   Using pip:

   ```bash
   pip install -e ".[dev]"
   ```

3. **Run tests and quality checks**:

   ```bash
   # Run all tests with coverage
   invoke pytest

   # Run all linting checks
   invoke lint

   # Run all checks (tests, linting, security, docs)
   invoke all

   # Show all available tasks and usage examples
   invoke help
   ```

### Code Quality

This project uses several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **ruff**: Linting and code analysis
- **pytest**: Testing with coverage
- **pre-commit**: Git hooks for automated checks

### Pre-commit Hooks

Pre-commit hooks provide automated code quality checks before commits. They ensure consistent code style and catch common issues early.

#### Installation

Install pre-commit hooks using invoke:

```bash
invoke pre-commit-install
```

#### Manual Usage

Run all pre-commit hooks manually on all files:

```bash
invoke pre-commit
```

Or run directly with poetry:

```bash
poetry run pre-commit run --all-files
```

#### Individual Hook Commands

You can also run individual checks manually:

```bash
invoke black          # Black formatting check
invoke isort          # Import sorting check
invoke flake8         # Flake8 linting
invoke mypy           # Type checking
invoke darglint       # Docstring linting (manual stage only)
```

#### Hook Configuration

Pre-commit hooks are configured in `.pre-commit-config.yaml` and use poetry to ensure all tools run in the correct virtual environment. The hooks include:

- **Formatting**: Black, isort
- **Linting**: Flake8, darglint, mypy
- **File checks**: End-of-file-fixer, trailing-whitespace, check-added-large-files
- **Config validation**: check-toml, check-yaml
- **Code modernization**: pyupgrade

#### Pre-commit vs Invoke

- **Pre-commit hooks**: Run automatically before commits, focus on file-level changes
- **Invoke tasks**: Run manually, provide comprehensive project-wide checks and testing
- **Both methods** use the same underlying tools and configuration for consistency

### Development Tasks (Invoke)

The project uses [Invoke](https://www.pyinvoke.org/) for task automation. Use `invoke --list` to see all available tasks, or `invoke help` for detailed usage examples.

**Common development tasks:**

- `invoke pytest` - Run all tests with coverage
- `invoke lint` - Run all linting checks (black, isort, flake8, mypy, darglint)
- `invoke pre-commit-install` - Install pre-commit hooks
- `invoke pre-commit` - Run all pre-commit hooks on all files
- `invoke test-unit` - Run only unit tests
- `invoke test-integration` - Run only integration tests
- `invoke black` - Run Black formatting check only
- `invoke mypy` - Run type checking only
- `invoke clean` - Clean build artifacts and cache
- `invoke all` - Run all checks (tests, linting, security, docs)

### Testing

```bash
# Run all tests with coverage
invoke pytest

# Run specific test types
invoke test-unit
invoke test-integration
invoke test-contract

# Run all checks (tests, linting, security, docs)
invoke all

# Show detailed usage examples
invoke help
```

### Contributing

Contributions are very welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Code of Conduct
- How to submit pull requests
- Development workflow
- Coding standards

## 📄 License

Distributed under the terms of the [GPL 3.0 license][license],
ORD Plan is free and open source software.

## 🐛 Issues

If you encounter any problems, please [file an issue][file an issue] along with a detailed description.

## 🙏 Credits

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

<!-- github-only -->

## 📚 Additional Resources

- [Full Documentation](https://ord-plan.readthedocs.io/)
- [Org-mode Guide](https://orgmode.org/guide/)
- [Cron Generator](https://crontab.guru/) - Interactive cron expression builder

## 🔗 Links

[license]: https://github.com/vonpupp/blob/main/LICENSE
[contributor guide]: https://github.com/vonpupp/blob/main/CONTRIBUTING.md
[command-line reference]: https://ord-plan.readthedocs.io/en/latest/usage.html
[cjolowicz]: https://github.com/cjolowicz
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/vonpupp/issues
[pip]: https://pip.pypa.io/
[poetry]: https://python-poetry.org/
[uv]: https://docs.astral.sh/uv/
