"""Pytest fixtures."""

import pytest
from pathlib import Path
from click.testing import CliRunner


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()
