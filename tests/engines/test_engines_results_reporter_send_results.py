# -*- coding: utf-8 -*-
"""Tests for results_reporter module, the TestRailResultsReporter class, send_results method"""

from unittest.mock import patch

import pytest
from faker import Faker

from testrail_api_reporter.engines.results_reporter import (  # pylint: disable=import-error,no-name-in-module
    TestRailResultsReporter,
)

fake = Faker()


@pytest.fixture
def reporter(tmp_path):
    """Fixture to return TestRailResultsReporter with a mocked TestRailAPI, fully configured and ready to send"""
    report = tmp_path / "junit-report.xml"
    report.write_text("<testsuites></testsuites>", encoding="utf-8")
    with patch("testrail_api_reporter.engines.results_reporter.TestRailAPI"):
        instance = TestRailResultsReporter(
            url=fake.url(), email=fake.email(), password=fake.password(), project_id=None, xml_report=str(report)
        )
    instance._TestRailResultsReporter__project_id = fake.random_int()  # pylint: disable=protected-access
    instance._TestRailResultsReporter__at_section = fake.random_int()  # pylint: disable=protected-access
    return instance


def test_send_results_missing_project_id(reporter):  # pylint: disable=redefined-outer-name
    """Without a project id, send_results should bail out early and return True"""
    reporter._TestRailResultsReporter__project_id = None  # pylint: disable=protected-access

    result = reporter.send_results()

    assert result is True


def test_send_results_missing_at_section(reporter):  # pylint: disable=redefined-outer-name
    """Without an automation section, send_results should bail out early and return True"""
    reporter._TestRailResultsReporter__at_section = None  # pylint: disable=protected-access

    result = reporter.send_results()

    assert result is True


def test_send_results_missing_xml_report(reporter):  # pylint: disable=redefined-outer-name
    """Without an existing xml report, send_results should bail out early and return True"""
    reporter._TestRailResultsReporter__xml_report = None  # pylint: disable=protected-access

    result = reporter.send_results()

    assert result is True


def test_send_results_success_with_title(reporter):  # pylint: disable=redefined-outer-name
    """A full run with an explicit title, closing the run, should delegate to prepare/add/close"""
    title = fake.sentence()
    run_id = fake.random_int()
    payload = [{"case_id": 1}]
    with patch.object(reporter, "_TestRailResultsReporter__prepare_payload", return_value=payload), patch.object(
        reporter, "_TestRailResultsReporter__prepare_runs", return_value=run_id
    ) as mock_prepare_runs, patch.object(
        reporter, "_TestRailResultsReporter__add_results", return_value=run_id
    ) as mock_add_results, patch.object(
        reporter, "_TestRailResultsReporter__close_run"
    ) as mock_close_run:
        result = reporter.send_results(title=title)

    assert result == run_id
    mock_prepare_runs.assert_called_once_with(cases=payload, title=title, run_id=None, run_name=None, delete_run=False)
    mock_add_results.assert_called_once_with(run_id=run_id, results=payload)
    mock_close_run.assert_called_once_with(run_id=run_id, title=title)


def test_send_results_success_no_close_run_name_priority(reporter):  # pylint: disable=redefined-outer-name
    """run_name should take priority over title, and close_run=False should skip closing the run"""
    run_name = fake.sentence()
    payload = [{"case_id": 1}]
    with patch.object(reporter, "_TestRailResultsReporter__prepare_payload", return_value=payload), patch.object(
        reporter, "_TestRailResultsReporter__prepare_runs", return_value=fake.random_int()
    ) as mock_prepare_runs, patch.object(
        reporter, "_TestRailResultsReporter__add_results", return_value=fake.random_int()
    ), patch.object(
        reporter, "_TestRailResultsReporter__close_run"
    ) as mock_close_run:
        reporter.send_results(title=fake.sentence(), run_name=run_name, close_run=False)

    assert mock_prepare_runs.call_args.kwargs["title"] == run_name
    mock_close_run.assert_not_called()
