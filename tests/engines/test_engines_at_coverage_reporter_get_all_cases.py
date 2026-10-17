# -*- coding: utf-8 -*-
"""Tests for at_coverage_reporter module, the ATCoverageReporter class, internal __get_all_cases method"""

from unittest.mock import patch

import pytest
from faker import Faker
from requests.exceptions import ReadTimeout

from testrail_api_reporter.engines.at_coverage_reporter import (  # pylint: disable=import-error,no-name-in-module
    ATCoverageReporter,
)

fake = Faker()


@pytest.fixture
def reporter():
    """Fixture to return ATCoverageReporter with a mocked TestRailAPI"""
    with patch("testrail_api_reporter.engines.at_coverage_reporter.TestRailAPI"):
        return ATCoverageReporter(url=fake.url(), email=fake.email(), password=fake.password(), project=fake.random_int())


def test_get_all_cases_single_page(reporter):  # pylint: disable=redefined-outer-name
    """A single page of cases should be returned as-is"""
    api = reporter._ATCoverageReporter__api  # pylint: disable=protected-access
    cases = [{"id": 1}, {"id": 2}]
    api.cases.get_cases.return_value = {"cases": cases, "_links": {"next": None}}

    result = reporter._ATCoverageReporter__get_all_cases()  # pylint: disable=protected-access,no-member

    assert result == cases


def test_get_all_cases_multiple_pages(reporter):  # pylint: disable=redefined-outer-name
    """Multiple pages of cases should be collected and concatenated"""
    api = reporter._ATCoverageReporter__api  # pylint: disable=protected-access
    page1 = {"cases": [{"id": 1}], "_links": {"next": "?offset=1&limit=1"}}
    page2 = {"cases": [{"id": 2}], "_links": {"next": None}}
    api.cases.get_cases.side_effect = [page1, page2]

    result = reporter._ATCoverageReporter__get_all_cases()  # pylint: disable=protected-access,no-member

    assert result == page1["cases"] + page2["cases"]
    assert api.cases.get_cases.call_count == 2


def test_get_all_cases_first_run_timeout_retries_then_succeeds(reporter):  # pylint: disable=redefined-outer-name
    """A ReadTimeout on the first page should be retried until it succeeds"""
    api = reporter._ATCoverageReporter__api  # pylint: disable=protected-access
    cases = [{"id": 1}]
    api.cases.get_cases.side_effect = [ReadTimeout("boom"), {"cases": cases, "_links": {"next": None}}]

    result = reporter._ATCoverageReporter__get_all_cases(retries=3)  # pylint: disable=protected-access,no-member

    assert result == cases
    assert api.cases.get_cases.call_count == 2


def test_get_all_cases_first_run_timeout_exhausted(reporter):  # pylint: disable=redefined-outer-name
    """A ReadTimeout on the first page, exhausting all retries, should raise ValueError"""
    api = reporter._ATCoverageReporter__api  # pylint: disable=protected-access
    api.cases.get_cases.side_effect = ReadTimeout("boom")

    with pytest.raises(ValueError, match="Get cases failed. Please validate your settings!"):
        reporter._ATCoverageReporter__get_all_cases(retries=1)  # pylint: disable=protected-access,no-member


def test_get_all_cases_first_run_generic_exception(reporter):  # pylint: disable=redefined-outer-name
    """A non-timeout failure on the first page should be wrapped in ValueError immediately"""
    api = reporter._ATCoverageReporter__api  # pylint: disable=protected-access
    api.cases.get_cases.side_effect = OSError("boom")

    with pytest.raises(ValueError, match="Get cases failed. Please validate your settings!"):
        reporter._ATCoverageReporter__get_all_cases()  # pylint: disable=protected-access,no-member


def test_get_all_cases_pagination_timeout_retries_then_succeeds(reporter):  # pylint: disable=redefined-outer-name
    """A ReadTimeout fetching the second page should be retried until it succeeds"""
    api = reporter._ATCoverageReporter__api  # pylint: disable=protected-access
    page1 = {"cases": [{"id": 1}], "_links": {"next": "?offset=1&limit=1"}}
    page2 = {"cases": [{"id": 2}], "_links": {"next": None}}
    api.cases.get_cases.side_effect = [page1, ReadTimeout("boom"), page2]

    result = reporter._ATCoverageReporter__get_all_cases(retries=3)  # pylint: disable=protected-access,no-member

    assert result == page1["cases"] + page2["cases"]
    assert api.cases.get_cases.call_count == 3


def test_get_all_cases_pagination_timeout_exhausted(reporter):  # pylint: disable=redefined-outer-name
    """A ReadTimeout fetching the second page, exhausting all retries, should raise ValueError"""
    api = reporter._ATCoverageReporter__api  # pylint: disable=protected-access
    page1 = {"cases": [{"id": 1}], "_links": {"next": "?offset=1&limit=1"}}
    api.cases.get_cases.side_effect = [page1, ReadTimeout("boom")]

    with pytest.raises(ValueError, match="Get cases failed. Please validate your settings!"):
        reporter._ATCoverageReporter__get_all_cases(retries=0)  # pylint: disable=protected-access,no-member


def test_get_all_cases_pagination_generic_exception(reporter):  # pylint: disable=redefined-outer-name
    """A non-timeout failure fetching the second page should be wrapped in ValueError"""
    api = reporter._ATCoverageReporter__api  # pylint: disable=protected-access
    page1 = {"cases": [{"id": 1}], "_links": {"next": "?offset=1&limit=1"}}
    api.cases.get_cases.side_effect = [page1, OSError("boom")]

    with pytest.raises(ValueError, match="Get cases failed. Please validate your settings!"):
        reporter._ATCoverageReporter__get_all_cases()  # pylint: disable=protected-access,no-member
