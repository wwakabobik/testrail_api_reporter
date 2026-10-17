# -*- coding: utf-8 -*-
"""Tests for content_generator module, the TestCaseContentGenerator class, init method"""

from logging import getLogger, INFO, WARNING, ERROR, FATAL
from os import path, remove
from random import choice
from unittest.mock import MagicMock, patch

import pytest
from faker import Faker

from testrail_api_reporter.engines.content_generator import (  # pylint: disable=import-error,no-name-in-module
    TestCaseContentGenerator,
)
from testrail_api_reporter.utils.logger_config import (  # pylint: disable=import-error,no-name-in-module
    setup_logger,
    DEFAULT_LOGGING_LEVEL,
)

fake = Faker()


@patch("testrail_api_reporter.engines.content_generator.TestRailAPI")
def test_content_generator_init_default_params(mock_api_class):
    """Init TestCaseContentGenerator with default parameters"""
    url = fake.url()
    email = fake.email()
    password = fake.password()
    project_id = fake.random_int()
    provider = MagicMock()

    generator = TestCaseContentGenerator(
        url=url, email=email, password=password, project_id=project_id, provider=provider
    )

    mock_api_class.assert_called_once_with(url, email, password)

    logger = getLogger("TestCaseContentGenerator")
    assert logger.level == DEFAULT_LOGGING_LEVEL
    assert path.exists("TestCaseContentGenerator.log")

    attributes = vars(generator)
    assert attributes["_TestCaseContentGenerator__project_id"] == project_id
    assert attributes["_TestCaseContentGenerator__suite_id"] is None
    assert attributes["_TestCaseContentGenerator__provider"] is provider
    assert attributes["_TestCaseContentGenerator__cases_by_automation_id"] == {}


@patch("testrail_api_reporter.engines.content_generator.TestRailAPI")
def test_content_generator_init_custom_logger(mock_api_class):  # pylint: disable=unused-argument
    """Init TestCaseContentGenerator with a custom logger"""
    logger_file = fake.file_name(extension="log")
    logger_name = fake.name()
    logger_level = choice((INFO, WARNING, ERROR, FATAL))
    try:
        logger = setup_logger(logger_name, logger_file, level=logger_level)
        TestCaseContentGenerator(
            url=fake.url(),
            email=fake.email(),
            password=fake.password(),
            project_id=fake.random_int(),
            provider=MagicMock(),
            logger=logger,
            log_level=INFO,
        )

        logger = getLogger(logger_name)
        assert logger.level == logger_level
        assert path.exists(logger_file)
    finally:
        if path.exists(logger_file):
            remove(logger_file)


def test_content_generator_init_no_credentials():
    """Init TestCaseContentGenerator without credentials should raise ValueError"""
    with pytest.raises(ValueError, match="No TestRails credentials are provided!"):
        TestCaseContentGenerator(url=None, email=None, password=None, project_id=1, provider=MagicMock())


@patch("testrail_api_reporter.engines.content_generator.TestRailAPI")
def test_content_generator_init_no_provider(mock_api_class):  # pylint: disable=unused-argument
    """Init TestCaseContentGenerator without an AI provider should raise ValueError"""
    with pytest.raises(ValueError, match="No AI provider is provided!"):
        TestCaseContentGenerator(
            url=fake.url(), email=fake.email(), password=fake.password(), project_id=fake.random_int(), provider=None
        )
