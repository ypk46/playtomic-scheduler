# Native imports
import json
import time
import logging

# 3rd party imports
import click
import schedule

# Project imports
from playtomic_scheduler.config import settings
from playtomic_scheduler.utils import directory
from playtomic_scheduler.helpers.reserver import Reserver
from playtomic_scheduler.helpers.playtomic import Playtomic

logger = logging.getLogger("playtomic-scheduler-cli")


@click.command("schedule")
@click.option(
    "-m",
    "--minutes",
    type=int,
    default=10,
    help="How often should the scheduler check for available courts (in minutes)",
)
def schedule_cmd(minutes: int):
    """
    Schedule reservation checks until a reservation is confirmed.
    """
    config_path = directory.setup_dir()
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

    days = config.get("days")
    hours = config.get("hours")
    duration = config.get("duration")

    if not days or not hours or not duration:
        logger.info("You need to provide all the required options.")
        return

    reserver = Reserver(playtomic, days, hours, duration)

    def reservation_check():
        """
        Check for available courts and reserve them if available.
        """
        reserver.playtomic.login()
        for tenant in settings.tenants:
            reserver.process_tenant(tenant)

    schedule.every(minutes).minutes.do(reservation_check)

    logger.info("Starting scheduler! Running checks every %s minutes...", minutes)
    while reserver.reservation_confirmed is False:
        schedule.run_pending()
        time.sleep(1)
