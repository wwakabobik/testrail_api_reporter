# -*- coding: utf-8 -*-
"""Tests for slack_sender module, the SlackSender class, init method"""

from logging import getLogger, INFO, WARNING, ERROR, FATAL
from os import path, remove
from random import choice

import pytest
from faker import Faker

from testrail_api_reporter.publishers.slack_sender import (  # pylint: disable=import-error,no-name-in-module
    SlackSender,
)
from testrail_api_reporter.utils.logger_config import (  # pylint: disable=import-error,no-name-in-module
    setup_logger,
    DEFAULT_LOGGING_LEVEL,
)

fake = Faker()


def test_slack_sender_init_default_params():
    """Init SlackSender with default parameters"""
    hook_url = fake.url()

    slack_sender = SlackSender(hook_url=hook_url)

    logger = getLogger("SlackSender")
    assert logger.level == DEFAULT_LOGGING_LEVEL
    assert path.exists("SlackSender.log")

    attributes = vars(slack_sender)
    assert attributes["_SlackSender__hook_url"] == hook_url
    assert attributes["_SlackSender__timeout"] == 5
    assert attributes["_SlackSender__verify"] is True


def test_slack_sender_init_custom_params():
    """Init SlackSender with custom parameters"""
    logger_file = fake.file_name(extension="log")
    logger_name = fake.name()
    logger_level = choice((INFO, WARNING, ERROR, FATAL))
    try:
        logger = setup_logger(logger_name, logger_file, level=logger_level)
        hook_url = fake.url()
        timeout = fake.random_int(min=1, max=60)
        verify = fake.boolean()

        slack_sender = SlackSender(
            hook_url=hook_url, timeout=timeout, verify=verify, logger=logger, log_level=INFO
        )

        logger = getLogger(logger_name)
        assert logger.level == logger_level
        assert path.exists(logger_file)

        attributes = vars(slack_sender)
        assert attributes["_SlackSender__hook_url"] == hook_url
        assert attributes["_SlackSender__timeout"] == timeout
        assert attributes["_SlackSender__verify"] == verify
    finally:
        if path.exists(logger_file):
            remove(logger_file)


def test_slack_sender_init_no_hook_url():
    """Init SlackSender without hook_url should raise ValueError"""
    with pytest.raises(ValueError, match="No Slack hook url provided, aborted!"):
        SlackSender()
