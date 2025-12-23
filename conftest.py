"""Pytest fixtures."""

import sys
from pathlib import Path

import pytest
from click.testing import CliRunner


src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()
