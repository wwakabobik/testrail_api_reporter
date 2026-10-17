# -*- coding: utf-8 -*-
"""Tests for results_reporter module, the TestRailResultsReporter class, init method"""

from logging import getLogger, INFO, WARNING, ERROR, FATAL
from os import path, remove
from random import choice
from unittest.mock import patch

import pytest
from faker import Faker

from testrail_api_reporter.engines.results_reporter import (  # pylint: disable=import-error,no-name-in-module
    TestRailResultsReporter,
)
from testrail_api_reporter.utils.logger_config import (  # pylint: disable=import-error,no-name-in-module
    setup_logger,
    DEFAULT_LOGGING_LEVEL,
)

fake = Faker()


def _found_section_response():
    """Response with the default automation section ('pytest') already present, single page"""
    return {"sections": [{"id": 42, "name": "pytest"}], "_links": {"next": None}}


@pytest.fixture
def xml_report(tmp_path):
    """Fixture to return a path to an existing (empty-ish) xml report file"""
    report = tmp_path / "junit-report.xml"
    report.write_text("<testsuites></testsuites>", encoding="utf-8")
    return str(report)


@patch("testrail_api_reporter.engines.results_reporter.TestRailAPI")
def test_results_reporter_init_default_params(mock_api_class, xml_report):  # pylint: disable=redefined-outer-name
    """Init TestRailResultsReporter with default parameters"""
    api = mock_api_class.return_value
    api.sections.get_sections.return_value = _found_section_response()

    url = fake.url()
    email = fake.email()
    password = fake.password()
    project_id = fake.random_int()

    reporter = TestRailResultsReporter(url=url, email=email, password=password, project_id=project_id, xml_report=xml_report)

    mock_api_class.assert_called_once_with(url, email, password)

    logger = getLogger("TestRailResultsReporter")
    assert logger.level == DEFAULT_LOGGING_LEVEL
    assert path.exists("TestRailResultsReporter.log")

    attributes = vars(reporter)
    assert attributes["_TestRailResultsReporter__xml_report"] == xml_report
    assert attributes["_TestRailResultsReporter__project_id"] == project_id
    assert attributes["_TestRailResultsReporter__at_section"] == 42


@patch("testrail_api_reporter.engines.results_reporter.TestRailAPI")
def test_results_reporter_init_custom_logger(mock_api_class, xml_report):  # pylint: disable=redefined-outer-name
    """Init TestRailResultsReporter with a custom logger"""
    api = mock_api_class.return_value
    api.sections.get_sections.return_value = _found_section_response()

    logger_file = fake.file_name(extension="log")
    logger_name = fake.name()
    logger_level = choice((INFO, WARNING, ERROR, FATAL))
    try:
        logger = setup_logger(logger_name, logger_file, level=logger_level)
        TestRailResultsReporter(
            url=fake.url(),
            email=fake.email(),
            password=fake.password(),
            project_id=fake.random_int(),
            xml_report=xml_report,
            logger=logger,
            log_level=INFO,
        )

        logger = getLogger(logger_name)
        assert logger.level == logger_level
        assert path.exists(logger_file)
    finally:
        if path.exists(logger_file):
            remove(logger_file)


def test_results_reporter_init_no_credentials():
    """Init TestRailResultsReporter without credentials should raise ValueError"""
    with pytest.raises(ValueError, match="No TestRails credentials are provided!"):
        TestRailResultsReporter(url=None, email=None, password=None, project_id=1)


@patch("testrail_api_reporter.engines.results_reporter.TestRailAPI")
def test_results_reporter_init_missing_xml_report(mock_api_class):
    """Init TestRailResultsReporter with a non-existent xml report should leave xml_report as None"""
    api = mock_api_class.return_value
    api.sections.get_sections.return_value = _found_section_response()

    reporter = TestRailResultsReporter(
        url=fake.url(),
        email=fake.email(),
        password=fake.password(),
        project_id=fake.random_int(),
        xml_report=fake.file_name(extension="xml"),
    )

    assert vars(reporter)["_TestRailResultsReporter__xml_report"] is None


@patch("testrail_api_reporter.engines.results_reporter.TestRailAPI")
def test_results_reporter_init_invalid_project(mock_api_class, xml_report):  # pylint: disable=redefined-outer-name
    """Init TestRailResultsReporter where the project check fails should leave project_id/at_section as None"""
    api = mock_api_class.return_value
    api.projects.get_project.side_effect = OSError("boom")

    reporter = TestRailResultsReporter(
        url=fake.url(), email=fake.email(), password=fake.password(), project_id=fake.random_int(), xml_report=xml_report
    )

    attributes = vars(reporter)
    assert attributes["_TestRailResultsReporter__project_id"] is None
    assert attributes["_TestRailResultsReporter__at_section"] is None


@patch("testrail_api_reporter.engines.results_reporter.TestRailAPI")
def test_results_reporter_init_invalid_suite(mock_api_class, xml_report):  # pylint: disable=redefined-outer-name
    """Init TestRailResultsReporter where the suite check fails should leave suite_id as None"""
    api = mock_api_class.return_value
    api.suites.get_suite.side_effect = OSError("boom")
    api.sections.get_sections.return_value = _found_section_response()

    reporter = TestRailResultsReporter(
        url=fake.url(),
        email=fake.email(),
        password=fake.password(),
        project_id=fake.random_int(),
        suite_id=fake.random_int(),
        xml_report=xml_report,
    )

    assert vars(reporter)["_TestRailResultsReporter__suite_id"] is None


@patch("testrail_api_reporter.engines.results_reporter.TestRailAPI")
def test_results_reporter_init_no_project_id_skips_section_lookup(mock_api_class, xml_report):  # pylint: disable=redefined-outer-name
    """Init TestRailResultsReporter with a project check that fails should also skip the section lookup"""
    api = mock_api_class.return_value
    api.projects.get_project.side_effect = OSError("boom")

    TestRailResultsReporter(
        url=fake.url(), email=fake.email(), password=fake.password(), project_id=fake.random_int(), xml_report=xml_report
    )

    api.sections.get_sections.assert_not_called()
