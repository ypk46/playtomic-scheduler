# Native imports
import os
import logging
from pathlib import Path

# Project imports
from playtomic_scheduler.config import settings


logger = logging.getLogger("playtomic-scheduler-cli")


def _get_default_dir():
    """
    Get default directory based OS user directory.
    """
    default_dir_path = os.path.join(os.path.expanduser("~"), ".playtomic-scheduler-cli")
    default_dir_path = Path(default_dir_path)
    default_dir_path.mkdir(parents=True, exist_ok=True)
    return default_dir_path


def setup_dir(path: str = None):
    """
    Setups a new directory based joining the PS CLI directory
    and the provided path.

    Arguments
        path: Sub-path to the directory you want to setup.

    Returns
        A Path object of the whole Playtomic Scheduler CLI directory and your provided path (if any).
    """
    config_path = settings.config_path

    # Set default SDK directory
    if not config_path:
        config_path = _get_default_dir()

    # Fallback to default SDK directory
    elif config_path and not os.path.exists(config_path):
        logger.warning(
            "Provided PLAYTOMIC_SCHEDULER_PATH does not exists. Using default directory."
        )
        config_path = _get_default_dir()

    # Use provided directory
    else:
        config_path = Path(config_path)

    if path:
        new_path = config_path.joinpath(path)
        new_path.mkdir(parents=True, exist_ok=True)
        return new_path

    return config_path
