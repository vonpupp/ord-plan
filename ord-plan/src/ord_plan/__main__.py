"""Command-line interface."""

import click
from .cli import cli_group


def main() -> None:
    """ORD Plan CLI entry point."""
    cli_group(prog_name="ord-plan")


if __name__ == "__main__":
    main()  # pragma: no cover
