# -*- coding: utf-8 -*-
"""Tests for the logger_config module"""

from logging import DEBUG, INFO, WARNING, ERROR, FATAL, FileHandler, StreamHandler
from random import choice, randint

from faker import Faker

from testrail_api_reporter.utils.logger_config import setup_logger, DEFAULT_LOGGING_LEVEL


fake = Faker()


def test_setup_logger_default_level(caplog):
    """Init logger with default level"""
    log_file = fake.file_name(extension="log")
    logger = setup_logger(fake.name(), str(log_file))

    assert logger.level == DEFAULT_LOGGING_LEVEL
    assert logger.level == DEBUG

    assert len(logger.handlers) == 2
    assert isinstance(logger.handlers[0], FileHandler)
    assert isinstance(logger.handlers[1], StreamHandler)

    message = str(fake.random_letters(randint(1, 10))) * randint(1, 10)
    logger.debug(message)
    with open(log_file, "r") as f:
        assert message in f.read()
    assert message in caplog.text


def test_setup_logger_custom_level(tmp_path):
    """Init logger with any other level"""
    log_file = fake.file_name(extension="log")
    log_level = choice((INFO, WARNING, ERROR, FATAL))
    logger = setup_logger(fake.name(), str(log_file), level=log_level)

    assert logger.level == log_level
