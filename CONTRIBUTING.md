# Contributor Guide

Thank you for your interest in improving this project.
This project is open-source under the [GPL 3.0 license] and
welcomes contributions in the form of bug reports, feature requests, and pull requests.

Here is a list of important resources for contributors:

- [Source Code]
- [Documentation]
- [Issue Tracker]
- [Code of Conduct]

[gpl 3.0 license]: https://opensource.org/licenses/GPL-3.0
[source code]: https://github.com/vonpupp/ord-plan
[documentation]: https://ord-plan.readthedocs.io/
[issue tracker]: https://github.com/vonpupp/issues

## How to report a bug

Report bugs on the [Issue Tracker].

When filing an issue, make sure to answer these questions:

- Which operating system and Python version are you using?
- Which version of this project are you using?
- What did you do?
- What did you expect to see?
- What did you see instead?

The best way to get your bug fixed is to provide a test case,
and/or steps to reproduce the issue.

## How to request a feature

Request features on the [Issue Tracker].

## How to set up your development environment

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

## How to test the project

### Using Invoke (Recommended)

Run tests and quality checks with Invoke:

```console
# Run all tests with coverage
$ invoke pytest

# Run all checks (tests, linting, security, docs)
$ invoke all

# Run specific test types
$ invoke test-unit
$ invoke test-integration

# Show all available tasks
$ invoke help
$ invoke --list
```

### Using Nox

Run full test suite:

```console
$ nox
```

List available Nox sessions:

```console
$ nox --list-sessions
```

You can also run a specific Nox session.
For example, invoke unit test suite like this:

```console
$ nox --session=tests
```

List the available Nox sessions:

```console
$ nox --list-sessions
```

You can also run a specific Nox session.
For example, invoke the unit test suite like this:

```console
$ nox --session=tests
```

Unit tests are located in the _tests_ directory,
and are written using the [pytest] testing framework.

[pytest]: https://pytest.readthedocs.io/

## How to submit changes

Open a [pull request] to submit changes to this project.

Your pull request needs to meet the following guidelines for acceptance:

- The test suite must pass without errors and warnings (use `invoke all` or `nox`).
- Include unit tests. This project maintains 100% code coverage.
- If your changes add functionality, update the documentation accordingly.

Feel free to submit early, though—we can always iterate on this.

To run linting and code formatting checks before committing your change, you can:

```console
# Using Invoke (recommended)
$ invoke lint

# Or install pre-commit as a Git hook
$ nox --session=pre-commit -- install
```

It is recommended to open an issue before starting work on anything.
This will allow a chance to talk it over with the owners and validate your approach.

[pull request]: https://github.com/vonpupp/pulls

<!-- github-only -->

[code of conduct]: CODE_OF_CONDUCT.md
