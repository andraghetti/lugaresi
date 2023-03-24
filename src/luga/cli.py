import logging
import importlib.metadata

from luga.dashboard import start_dashboard

from rich import print
import rich_click as click

click.rich_click.USE_RICH_MARKUP = True


@click.group()
def luga():
    logging.basicConfig(level=logging.INFO)
    pass


@luga.command()
def version():
    """Print version and exit."""
    version = importlib.metadata.version("luga")
    print(f"Version: {version}")


@luga.command()
@click.option(
    "-d",
    "--develop",
    type=bool,
    is_flag=True,
    help="Enables development mode on the dashboard, allowing to update the python package.",
    default=False,
)
def dashboard(develop: bool):
    """
    Start dashboard.
    """
    start_dashboard(develop=develop)


if __name__ == "__main__":
    luga()
