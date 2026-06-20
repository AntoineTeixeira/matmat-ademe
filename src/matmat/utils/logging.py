"""
Presentation
************
This module is the MatMat logging module.
It provides methods to configure logging and to log messages during the
program execution.

Content
*******
- Functions:
    - :meth:`configure_logging`
    - :meth:`log_title`
    - :meth:`error`
    - :meth:`warning`
    - :meth:`info`
    - :meth:`verbose`
    - :meth:`debug`
"""

__all__ = [
    "configure_logging",
    "log_title",
    "error",
    "warning",
    "info",
    "verbose",
    "debug",
]

import sys
import logging

from matmat.utils import config

LOGGER_NAME = "MatMat"
LOGGER_FORMAT = "%(asctime)s:%(levelname)s:%(message)s"


class CustomFormatter(logging.Formatter):
    """Custom Formatter does these 2 things:
    1. Overrides 'funcName' with the value of 'func_name_override',
       if it exists.
    2. Overrides 'filename' with the value of 'file_name_override',
       if it exists.
    """

    def format(self, record):
        if hasattr(record, "func_name_override"):
            record.funcName = record.func_name_override
        if hasattr(record, "file_name_override"):
            record.filename = record.file_name_override
        return super().format(record)


logger = logging.getLogger(LOGGER_NAME)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(CustomFormatter(LOGGER_FORMAT))
file_handler = logging.FileHandler(filename=config.LOG_FILE, mode="w")
file_handler.setFormatter(CustomFormatter(LOGGER_FORMAT))


def configure_logging():
    """
    Configure the logger with the logging level defined in the module `config`.
    This method shall be called before any logging operation.
    """
    logging.basicConfig(
        handlers=[stream_handler, file_handler], level=config.LOGGER_LEVEL
    )


def get_logger() -> logging.Logger:
    return logger


def log_title(title: str, symbol: str = "#", is_main: bool = False):
    """
    Log a formatted title with optional decorative borders.

    Parameters:
        title (str):
            The title text to log.
        symbol (str):
            Character used for borders (default is "#").
        is_main (bool):
            If True, adds empty borders above and below the title
            (default is False).
    """
    width = max(len(title) + 4, 40)  # 4 = "symbol " + " symbol"
    border = symbol * width
    empty_border = symbol + (" " * (width - 2)) + symbol
    title = f"{symbol} {title.upper().center(width - 4)} {symbol}"
    get_logger().info(border)
    if is_main:
        get_logger().info(empty_border)
    get_logger().info(title)
    if is_main:
        get_logger().info(empty_border)
    get_logger().info(border)


# Verbosity order
# 0. Error
# 1. Warning
# 2. Info
# 3. Verbose
# 4. Debug


def error(msg: str):
    get_logger().error(msg)
    if config.STOP_ON_ERROR:
        sys.exit(1)


def warning(msg: str):
    get_logger().warning(msg)


def info(msg: str):
    get_logger().info(msg)


def verbose(msg: str):
    if config.VERBOSE or config.LOGGER_LEVEL == logging.DEBUG:
        get_logger().info(msg)


def debug(msg: str):
    get_logger().debug(msg)
