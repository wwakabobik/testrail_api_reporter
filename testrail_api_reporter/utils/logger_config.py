# -*- coding: utf-8 -*-
"""Logger configuration"""

import logging
import sys

DEFAULT_LOGGING_LEVEL = logging.DEBUG


def setup_logger(name: str, log_file: str, level=logging.DEBUG):
    """
    Method to setup logger

    :param name: (string) Name of the logger.
    :param log_file: path to log_file
    :param level: logging level. Default is logging.DEBUG
    :returns: logger object
    """
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
