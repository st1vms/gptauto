"""Logging module utility"""
from logging import basicConfig, getLogger, INFO, Logger, StreamHandler
from colorlog import ColoredFormatter

LOGGER_NAME = "askgpt"

__LOG_FORMAT = """\
\033[1m\033[37m[%(asctime)s]\033[0m (%(log_color)s%(levelname)s%(reset)s): %(message)s\
"""

__LOG_FORMATTER = ColoredFormatter(
    __LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S",
    reset=True,
    log_colors={
        "ERROR": "red",
        "INFO": "green",
        "WARNING": "yellow",
        "CRITICAL": "red",
        "DEBUG": "blue",
    },
    secondary_log_colors={},
    style="%",
)

# Create a logger and set the formatter
__LOG_HANDLER = StreamHandler()
__LOG_HANDLER.setFormatter(__LOG_FORMATTER)
basicConfig(level=INFO, handlers=[__LOG_HANDLER])
log: Logger = getLogger(LOGGER_NAME)
