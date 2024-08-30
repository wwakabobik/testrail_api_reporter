# -*- coding: utf-8 -*-
"""Tests for the logger_config module"""

from logging import DEBUG, INFO, WARNING, ERROR, FATAL, FileHandler, StreamHandler
from os import path, remove
from random import choice

from faker import Faker

from testrail_api_reporter.utils.logger_config import (  # pylint: disable=import-error,no-name-in-module
    setup_logger,
    DEFAULT_LOGGING_LEVEL,
)

fake = Faker()


def test_setup_logger_default_level():
    """Init logger with default level"""
    log_file = fake.file_name(extension="log")
    try:
        logger = setup_logger(fake.name(), str(log_file))

        assert logger.level == DEFAULT_LOGGING_LEVEL
        assert logger.level == DEBUG

        assert len(logger.handlers) == 2
        assert isinstance(logger.handlers[0], FileHandler)
        assert isinstance(logger.handlers[1], StreamHandler)

        message = fake.name()
        logger.debug(message)
        with open(log_file, "r", encoding="utf-8") as readable_file:
            assert message in readable_file.read()
    finally:
        if path.exists(log_file):
            remove(log_file)


def test_setup_logger_custom_level():
    """Init logger with any other level"""
    log_file = fake.file_name(extension="log")
    try:
        log_level = choice((INFO, WARNING, ERROR, FATAL))
        logger = setup_logger(fake.name(), str(log_file), level=log_level)

        assert logger.level == log_level
    finally:
        if path.exists(log_file):
            remove(log_file)
