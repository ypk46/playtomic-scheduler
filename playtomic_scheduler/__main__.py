# Native imports
import logging

# 3rd party imports
import click

# Project imports
from playtomic_scheduler import __version__
from playtomic_scheduler.commands import *  # pylint: disable=W0401


# Enable logging
logger = logging.getLogger("playtomic-scheduler-cli")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


@click.group()
@click.version_option(__version__.version)
def cli():
    """
    Playomic Scheduler CLI.
    """


# Add commands
cli.add_command(init)
cli.add_command(reserve)
cli.add_command(schedule_cmd)

if __name__ == "__main__":
    cli()
