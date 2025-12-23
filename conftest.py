"""Pytest fixtures."""

from pathlib import Path
from sys import path

import pytest
from click.testing import CliRunner


src_path = Path(__file__).parent / "src"
if str(src_path) not in path:
    path.insert(0, str(src_path))


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()
