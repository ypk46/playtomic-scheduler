import json
import socket
import logging
from typing import Union


class ContextFilter(logging.Filter):
    hostname = socket.gethostname()

    def filter(self, record):
        record.hostname = ContextFilter.hostname
        return True


class CustomFormatter(logging.Formatter):
    def __init__(
        self,
        datefmt: Union[str, None] = None,
        name: str = "flask-app",
        env: str = "dev",
    ) -> None:
        self.name = name
        self.env = env
        super().__init__(datefmt=datefmt)

    def format(self, record):
        # Prepare log message
        is_text = isinstance(record.msg, (str))
        record.message = record.getMessage() if is_text else record.msg
        record.asctime = self.formatTime(record, self.datefmt)
        record.stack_info = self.formatStack(record.stack_info)

        # Prepare exception message
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        # Prepare json logging
        data = {"msg": record.message, "level": record.levelname}
        if record.exc_text:
            data["exception"] = record.exc_text

        return f"{record.asctime} {self.name} {self.name}-{self.env} {json.dumps(data)}"


def init_logger(
    logger: logging.Logger,
    name: str = "flask-app",
    env: str = "dev",
    level: int = logging.INFO,
) -> logging.Logger:
    """
    Initialize the logger using a custom formatter and filter.
    """
    # Create logger
    logger.propagate = False
    logger.setLevel(level)

    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # Create formatter
    formatter = CustomFormatter("%b %d %H:%M:%S", name, env)
    ch.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(ch)
