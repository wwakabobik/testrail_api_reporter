# -*- coding: utf-8 -*-
"""Tests for results_reporter module, the TestRailResultsReporter class, internal __get_all_auto_cases method"""

from unittest.mock import patch

import pytest
from faker import Faker
from requests.exceptions import ReadTimeout
from testrail_api import StatusCodeError

from testrail_api_reporter.engines.results_reporter import (  # pylint: disable=import-error,no-name-in-module
    TestRailResultsReporter,
)

fake = Faker()


def _status_code_error(status_code):
    """Build a StatusCodeError with a given status_code attribute attached"""
    error = StatusCodeError(f"status {status_code}")
    error.status_code = status_code
    return error


@pytest.fixture
def reporter(tmp_path):
    """Fixture to return TestRailResultsReporter with a mocked TestRailAPI, project checks skipped at init"""
    report = tmp_path / "junit-report.xml"
    report.write_text("<testsuites></testsuites>", encoding="utf-8")
    with patch("testrail_api_reporter.engines.results_reporter.TestRailAPI"):
        return TestRailResultsReporter(
            url=fake.url(), email=fake.email(), password=fake.password(), project_id=None, xml_report=str(report)
        )


def test_get_all_auto_cases_single_page(reporter):  # pylint: disable=redefined-outer-name
    """A single page of cases should keep only cases with a non-None custom_automation_id"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    cases = [{"id": 1, "custom_automation_id": "pkg.test_a"}, {"id": 2, "custom_automation_id": None}]
    api.cases.get_cases.return_value = {"cases": cases, "_links": {"next": None}}

    result = reporter._TestRailResultsReporter__get_all_auto_cases()  # pylint: disable=protected-access,no-member

    assert result == [{"id": 1, "custom_automation_id": "pkg.test_a"}]


def test_get_all_auto_cases_multiple_pages(reporter):  # pylint: disable=redefined-outer-name
    """Multiple pages of cases should be collected and concatenated"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    page1 = {"cases": [{"id": 1, "custom_automation_id": "pkg.a"}], "_links": {"next": "?page=2&offset=1&limit=1"}}
    page2 = {"cases": [{"id": 2, "custom_automation_id": "pkg.b"}], "_links": {"next": None}}
    api.cases.get_cases.side_effect = [page1, page2]

    result = reporter._TestRailResultsReporter__get_all_auto_cases()  # pylint: disable=protected-access,no-member

    assert result == page1["cases"] + page2["cases"]


def test_get_all_auto_cases_first_run_read_timeout_retries_then_succeeds(
    reporter,
):  # pylint: disable=redefined-outer-name
    """A ReadTimeout on the first page should be retried until it succeeds"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    cases = [{"id": 1, "custom_automation_id": "pkg.a"}]
    api.cases.get_cases.side_effect = [ReadTimeout("boom"), {"cases": cases, "_links": {"next": None}}]

    # pylint: disable=protected-access,no-member
    result = reporter._TestRailResultsReporter__get_all_auto_cases(retries=3)

    assert result == cases


def test_get_all_auto_cases_first_run_read_timeout_exhausted(reporter):  # pylint: disable=redefined-outer-name
    """A ReadTimeout on the first page, exhausting all retries, should raise ValueError"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.cases.get_cases.side_effect = ReadTimeout("boom")

    with pytest.raises(ValueError, match="Get cases failed. Please validate your settings!"):
        reporter._TestRailResultsReporter__get_all_auto_cases(retries=0)  # pylint: disable=protected-access,no-member


def test_get_all_auto_cases_first_run_status_code_504_retries_then_succeeds(
    reporter,
):  # pylint: disable=redefined-outer-name
    """A 504 StatusCodeError on the first page should be retried just like a ReadTimeout"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    cases = [{"id": 1, "custom_automation_id": "pkg.a"}]
    api.cases.get_cases.side_effect = [_status_code_error(504), {"cases": cases, "_links": {"next": None}}]

    # pylint: disable=protected-access,no-member
    result = reporter._TestRailResultsReporter__get_all_auto_cases(retries=3)

    assert result == cases


def test_get_all_auto_cases_first_run_other_status_code_crashes(reporter):  # pylint: disable=redefined-outer-name
    """A non-504 StatusCodeError on the first page is swallowed by the except, and the unset response then
    crashes the subsequent, unconditional 'cases = response["cases"]' line (pre-existing behaviour)"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.cases.get_cases.side_effect = _status_code_error(404)

    with pytest.raises(TypeError):
        reporter._TestRailResultsReporter__get_all_auto_cases()  # pylint: disable=protected-access,no-member


def test_get_all_auto_cases_first_run_generic_exception(reporter):  # pylint: disable=redefined-outer-name
    """A non-timeout, non-status-code failure on the first page should be logged and return None"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.cases.get_cases.side_effect = OSError("boom")

    result = reporter._TestRailResultsReporter__get_all_auto_cases()  # pylint: disable=protected-access,no-member

    assert result is None


def test_get_all_auto_cases_pagination_read_timeout_retries_then_succeeds(
    reporter,
):  # pylint: disable=redefined-outer-name
    """A ReadTimeout fetching the second page should be retried until it succeeds"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    page1 = {"cases": [{"id": 1, "custom_automation_id": "pkg.a"}], "_links": {"next": "?page=2&offset=1&limit=1"}}
    page2 = {"cases": [{"id": 2, "custom_automation_id": "pkg.b"}], "_links": {"next": None}}
    api.cases.get_cases.side_effect = [page1, ReadTimeout("boom"), page2]

    # pylint: disable=protected-access,no-member
    result = reporter._TestRailResultsReporter__get_all_auto_cases(retries=3)

    assert result == page1["cases"] + page2["cases"]


def test_get_all_auto_cases_pagination_read_timeout_exhausted(reporter):  # pylint: disable=redefined-outer-name
    """A ReadTimeout fetching the second page, exhausting all retries, should raise ValueError"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    page1 = {"cases": [{"id": 1, "custom_automation_id": "pkg.a"}], "_links": {"next": "?page=2&offset=1&limit=1"}}
    api.cases.get_cases.side_effect = [page1, ReadTimeout("boom")]

    with pytest.raises(ValueError, match="Get cases failed. Please validate your settings!"):
        reporter._TestRailResultsReporter__get_all_auto_cases(retries=0)  # pylint: disable=protected-access,no-member


def test_get_all_auto_cases_pagination_other_status_code_is_swallowed(reporter):  # pylint: disable=redefined-outer-name
    """A non-504 StatusCodeError fetching the second page is swallowed; the stale previous page is re-used
    (duplicated) until a later, successful call finally advances pagination (pre-existing behaviour)"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    page1 = {"cases": [{"id": 1, "custom_automation_id": "pkg.a"}], "_links": {"next": "?page=2&offset=1&limit=1"}}
    page2 = {"cases": [{"id": 2, "custom_automation_id": "pkg.b"}], "_links": {"next": None}}
    api.cases.get_cases.side_effect = [page1, _status_code_error(404), page2]

    result = reporter._TestRailResultsReporter__get_all_auto_cases()  # pylint: disable=protected-access,no-member

    # page1's case is counted twice: once normally, once more while the stale response was re-used
    assert result == page1["cases"] + page1["cases"] + page2["cases"]
