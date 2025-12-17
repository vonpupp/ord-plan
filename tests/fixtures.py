"""Helper utilities for accessing test fixtures."""

import os
from pathlib import Path
from typing import Union


def get_fixture_path(filename: str) -> Path:
    """Get the absolute path to a test fixture file.

    Args:
        filename: Name of the fixture file in tests/fixtures/

    Returns:
        Path to the fixture file
    """
    current_dir = Path(__file__).parent
    return current_dir / "fixtures" / filename


def read_fixture(filename: str) -> str:
    """Read the contents of a fixture file.

    Args:
        filename: Name of the fixture file in tests/fixtures/

    Returns:
        Contents of the fixture file as string
    """
    return get_fixture_path(filename).read_text(encoding="utf-8")


def write_to_fixture(filename: str, content: str) -> None:
    """Write content to a fixture file (for temporary fixtures).

    Args:
        filename: Name of the fixture file
        content: Content to write
    """
    get_fixture_path(filename).write_text(content, encoding="utf-8")


def list_fixtures() -> list[str]:
    """List all available fixture files.

    Returns:
        List of fixture filenames
    """
    fixtures_dir = get_fixture_path("")
    return [f.name for f in fixtures_dir.iterdir() if f.is_file()]
