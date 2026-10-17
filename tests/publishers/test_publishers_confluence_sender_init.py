# -*- coding: utf-8 -*-
"""Tests for confluence_sender module, the ConfluenceSender class, init method"""

from logging import getLogger, INFO, WARNING, ERROR, FATAL
from os import path, remove
from random import choice, randint
from unittest.mock import patch, Mock

import pytest
from faker import Faker

from testrail_api_reporter.publishers.confluence_sender import (  # pylint: disable=import-error,no-name-in-module
    ConfluenceSender,
)
from testrail_api_reporter.utils.logger_config import (  # pylint: disable=import-error,no-name-in-module
    setup_logger,
    DEFAULT_LOGGING_LEVEL,
)

fake = Faker()


@patch("testrail_api_reporter.publishers.confluence_sender.Confluence")
def test_confluence_sender_init_default_params(mock_confluence):
    """Init ConfluenceSender with default parameters"""
    url = fake.url()
    username = fake.email()
    password = fake.password()
    type_platforms = [{"name": fake.word(), "sections": [randint(1, 10000)]}]

    sender = ConfluenceSender(url=url, username=username, password=password, type_platforms=type_platforms)

    mock_confluence.assert_called_once_with(url=url, username=username, password=password)

    logger = getLogger("ConfluenceReporter")
    assert logger.level == DEFAULT_LOGGING_LEVEL
    assert path.exists("ConfluenceReporter.log")

    attributes = vars(sender)
    assert attributes["_ConfluenceSender__confluence_page"] is None
    assert attributes["_ConfluenceSender__type_platforms"] == type_platforms


@patch("testrail_api_reporter.publishers.confluence_sender.Confluence")
def test_confluence_sender_init_custom_params(mock_confluence):  # pylint: disable=unused-argument
    """Init ConfluenceSender with custom parameters"""
    logger_file = fake.file_name(extension="log")
    logger_name = fake.name()
    logger_level = choice((INFO, WARNING, ERROR, FATAL))
    try:
        logger = setup_logger(logger_name, logger_file, level=logger_level)
        confluence_page = fake.word()
        automation_platforms = [{"name": fake.word(), "sections": [randint(1, 10000)]}]
        plotly_engine = Mock()

        sender = ConfluenceSender(
            url=fake.url(),
            username=fake.email(),
            password=fake.password(),
            confluence_page=confluence_page,
            automation_platforms=automation_platforms,
            plotly_engine=plotly_engine,
            logger=logger,
            log_level=INFO,
        )

        logger = getLogger(logger_name)
        assert logger.level == logger_level
        assert path.exists(logger_file)

        attributes = vars(sender)
        assert attributes["_ConfluenceSender__confluence_page"] == confluence_page
        assert attributes["_ConfluenceSender__automation_platforms"] == automation_platforms
        assert attributes["_ConfluenceSender__plotly"] is plotly_engine
    finally:
        if path.exists(logger_file):
            remove(logger_file)


def test_confluence_sender_init_no_credentials():
    """Init ConfluenceSender without credentials should raise ValueError"""
    with pytest.raises(ValueError, match="No confluence credentials are provided!"):
        ConfluenceSender()
