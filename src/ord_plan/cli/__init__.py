"""Main CLI group for ord-plan."""

import click

from .generate import generate


@click.group()
@click.version_option()
def cli_group() -> None:
    """ORD Plan - Generate org-mode events from cron rules."""


# Add generate command
cli_group.add_command(generate, name="generate")
