# -*- coding: utf-8 -*-
"""Tests for at_coverage_reporter module, the ATCoverageReporter class, internal __get_all_sections method"""

from unittest.mock import patch

import pytest
from faker import Faker

from testrail_api_reporter.engines.at_coverage_reporter import (  # pylint: disable=import-error,no-name-in-module
    ATCoverageReporter,
)

fake = Faker()


@pytest.fixture
def reporter():
    """Fixture to return ATCoverageReporter with a mocked TestRailAPI"""
    with patch("testrail_api_reporter.engines.at_coverage_reporter.TestRailAPI"):
        return ATCoverageReporter(
            url=fake.url(), email=fake.email(), password=fake.password(), project=fake.random_int()
        )


def test_get_all_sections_no_project(reporter):  # pylint: disable=redefined-outer-name
    """Call __get_all_sections without a project (none set at init either) should raise ValueError"""
    reporter._ATCoverageReporter__project = None  # pylint: disable=protected-access
    with pytest.raises(ValueError, match="No project specified, report aborted!"):
        reporter._ATCoverageReporter__get_all_sections()  # pylint: disable=protected-access,no-member


def test_get_all_sections_api_failure(reporter):  # pylint: disable=redefined-outer-name
    """A failure fetching sections should be logged and return None"""
    api = reporter._ATCoverageReporter__api  # pylint: disable=protected-access
    api.sections.get_sections.side_effect = OSError("boom")

    result = reporter._ATCoverageReporter__get_all_sections()  # pylint: disable=protected-access,no-member

    assert result is None


def test_get_all_sections_single_page(reporter):  # pylint: disable=redefined-outer-name
    """A single page of sections should be returned as-is"""
    api = reporter._ATCoverageReporter__api  # pylint: disable=protected-access
    sections = [{"id": 1, "parent_id": None}, {"id": 2, "parent_id": 1}]
    api.sections.get_sections.return_value = {"sections": sections, "_links": {"next": None}}

    result = reporter._ATCoverageReporter__get_all_sections()  # pylint: disable=protected-access,no-member

    assert result == sections
    api.sections.get_sections.assert_called_once()


def test_get_all_sections_multiple_pages(reporter):  # pylint: disable=redefined-outer-name
    """Multiple pages of sections should be collected and concatenated"""
    api = reporter._ATCoverageReporter__api  # pylint: disable=protected-access
    page1 = {"sections": [{"id": 1, "parent_id": None}], "_links": {"next": "?offset=1&limit=1"}}
    page2 = {"sections": [{"id": 2, "parent_id": None}], "_links": {"next": None}}
    api.sections.get_sections.side_effect = [page1, page2]

    result = reporter._ATCoverageReporter__get_all_sections(  # pylint: disable=protected-access,no-member
        project_id=fake.random_int(), suite_id=fake.random_int()
    )

    assert result == page1["sections"] + page2["sections"]
    assert api.sections.get_sections.call_count == 2
