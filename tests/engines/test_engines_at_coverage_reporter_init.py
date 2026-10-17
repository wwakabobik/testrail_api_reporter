# -*- coding: utf-8 -*-
"""Tests for at_coverage_reporter module, the ATCoverageReporter class, init method"""

from logging import getLogger, INFO, WARNING, ERROR, FATAL
from os import path, remove
from random import choice, randint
from unittest.mock import patch

import pytest
from faker import Faker

from testrail_api_reporter.engines.at_coverage_reporter import (  # pylint: disable=import-error,no-name-in-module
    ATCoverageReporter,
)
from testrail_api_reporter.utils.logger_config import (  # pylint: disable=import-error,no-name-in-module
    setup_logger,
    DEFAULT_LOGGING_LEVEL,
)

fake = Faker()


@patch("testrail_api_reporter.engines.at_coverage_reporter.TestRailAPI")
def test_at_coverage_reporter_init_default_params(mock_api):
    """Init ATCoverageReporter with default parameters"""
    url = fake.url()
    email = fake.email()
    password = fake.password()

    reporter = ATCoverageReporter(url=url, email=email, password=password)

    mock_api.assert_called_once_with(url=url, email=email, password=password)

    logger = getLogger("ATCoverageReporter")
    assert logger.level == DEFAULT_LOGGING_LEVEL
    assert path.exists("ATCoverageReporter.log")

    attributes = vars(reporter)
    assert attributes["_ATCoverageReporter__project"] is None
    assert attributes["_ATCoverageReporter__priority"] is None
    assert attributes["_ATCoverageReporter__suite_id"] is None


@patch("testrail_api_reporter.engines.at_coverage_reporter.TestRailAPI")
def test_at_coverage_reporter_init_custom_params(mock_api):  # pylint: disable=unused-argument
    """Init ATCoverageReporter with custom parameters"""
    logger_file = fake.file_name(extension="log")
    logger_name = fake.name()
    logger_level = choice((INFO, WARNING, ERROR, FATAL))
    try:
        logger = setup_logger(logger_name, logger_file, level=logger_level)
        project = fake.random_int()
        priority = fake.random_int()
        suite_id = fake.random_int()
        type_platforms = [{"name": fake.word(), "sections": [randint(1, 10000)]}]
        automation_platforms = [{"name": fake.word(), "sections": [randint(1, 10000)]}]

        reporter = ATCoverageReporter(
            url=fake.url(),
            email=fake.email(),
            password=fake.password(),
            priority=priority,
            project=project,
            type_platforms=type_platforms,
            automation_platforms=automation_platforms,
            suite_id=suite_id,
            logger=logger,
            log_level=INFO,
        )

        logger = getLogger(logger_name)
        assert logger.level == logger_level
        assert path.exists(logger_file)

        attributes = vars(reporter)
        assert attributes["_ATCoverageReporter__project"] == project
        assert attributes["_ATCoverageReporter__priority"] == priority
        assert attributes["_ATCoverageReporter__suite_id"] == suite_id
        assert attributes["_ATCoverageReporter__type_platforms"] == type_platforms
        assert attributes["_ATCoverageReporter__automation_platforms"] == automation_platforms
    finally:
        if path.exists(logger_file):
            remove(logger_file)


def test_at_coverage_reporter_init_no_credentials():
    """Init ATCoverageReporter without credentials should raise ValueError"""
    with pytest.raises(ValueError, match="No TestRails credentials are provided!"):
        ATCoverageReporter(url=None, email=None, password=None)
