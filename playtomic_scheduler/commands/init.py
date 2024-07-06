# Native imports
import os
import json
import logging

# 3rd party imports
import click
from requests.exceptions import HTTPError

# Project imports
from playtomic_scheduler.utils.dir import setup_dir
from playtomic_scheduler.helpers.playtomic import Playtomic

logger = logging.getLogger("playtomic-scheduler-cli")


@click.command("init")
def init():
    """
    Initialize Playtomic Scheduler CLI.
    """
    config_dir_path = setup_dir()
    config_file_path = os.path.join(config_dir_path, "config.json")

    # Check if configuration file already exists
    if os.path.exists(config_file_path):
        logger.info("Configuration file already exists. Skipping initialization.")
        logger.info(
            "If you want to re-initialize. Delete the file %s", config_file_path
        )
        return

    email = click.prompt(
        "Playtomic account email address",
        type=str,
    )
    password = click.prompt(
        "Playtomic account password",
        type=str,
        hide_input=True,
    )
    playtomic = Playtomic(email, password)

    try:
        playtomic.login()
    except HTTPError as err:
        if err.response.status_code == 401:
            click.echo("Wrong credentials provided.")
            return

        click.echo("An error occurred while trying to login.")
        return

    # Store credentials in configuration object
    click.echo("Login successfully to your Playtomic account.\n")
    config = {"email": email, "password": password}

    # Setup default values if user wants to
    should_setup_default = click.prompt(
        "Would you like to setup default values? (Y/n)",
        type=bool,
        default="Y",
    )
    if should_setup_default:
        days = click.prompt(
            "Which days of the week would you like to reserve courts? (e.g. 2,3 for Tue and Wed)",
            type=str,
        )

        hours = click.prompt(
            "At which starting hours would you like to reserve courts? (e.g. 20:00,20:30 for 8:00 PM or 8:30 PM)",
            type=str,
        )

        duration = click.prompt(
            "How many hours would you like to reserve the court for? ()",
            type=click.Choice(["1", "1.5", "2"]),
            default="1.5",
        )

        config["days"] = days
        config["hours"] = hours
        config["duration"] = duration

    with open(config_file_path, "w") as config_file:
        config_file.write(json.dumps(config))
