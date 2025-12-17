"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """ORD Plan."""


if __name__ == "__main__":
    main(prog_name="ord-plan")  # pragma: no cover
