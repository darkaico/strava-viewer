import logging
import os

from strava_viewer import BASE_DIR


def build_logger(logger_name):
    """Create and configure a default marvel bot tool logger."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    _add_file_handler(logger, logger_name)

    return logger


def _add_file_handler(logger: logging.Logger, logger_name: str):
    # create file handler which logs even debug messages
    log_filename = f"{BASE_DIR}/logs/{logger_name}.log"
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)

    fh = logging.FileHandler(log_filename)
    fh.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
