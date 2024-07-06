# Native imports
import json
import logging
from typing import Text, Optional

# 3rd party imports
import click

# Project imports
from playtomic_scheduler.utils.dir import setup_dir
from playtomic_scheduler.helpers.playtomic import Playtomic

logger = logging.getLogger("playtomic-scheduler-cli")


@click.command("reserve")
@click.option(
    "-d",
    "--days",
    type=str,
    required=False,
    help="Which days of the week would you like to reserve courts? (e.g. 2,3 for Tue and Wed)",
)
@click.option(
    "-h",
    "--hours",
    type=str,
    required=False,
    help="At which starting hours would you like to reserve courts? (e.g. 20:00)",
)
@click.option(
    "-u",
    "--duration",
    type=click.Choice(["1", "1.5", "2"]),
    required=False,
    help="How many hours would you like to reserve the court for",
)
def reserve(
    days: Optional[Text],
    hours: Optional[Text],
    duration: Optional[Text],
):
    """
    Reserve court through Playtomic based on provided configuration.
    """
    config_path = setup_dir()
    config_file_path = config_path.joinpath("config.json")

    if not config_file_path.exists():
        logger.info(
            "You need to initialize the CLI first. Run `playtomic-scheduler init`."
        )
        return

    with open(config_file_path, "r") as config_file:
        config = json.load(config_file)

    playtomic = Playtomic(config["email"], config["password"])
    playtomic.login()

    days = days or config.get("days")
    hours = hours or config.get("hours")
    duration = duration or config.get("duration")

    if not days or not hours or not duration:
        logger.info("You need to provide all the required options.")
        return
