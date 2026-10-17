# -*- coding: utf-8 -*-
"""Tests for results_reporter module, the TestRailResultsReporter class, internal __ensure_automation_section method"""

from unittest.mock import patch

import pytest
from faker import Faker

from testrail_api_reporter.engines.results_reporter import (  # pylint: disable=import-error,no-name-in-module
    TestRailResultsReporter,
)

fake = Faker()


@pytest.fixture
def reporter(tmp_path):
    """Fixture to return TestRailResultsReporter with a mocked TestRailAPI, project checks skipped at init"""
    report = tmp_path / "junit-report.xml"
    report.write_text("<testsuites></testsuites>", encoding="utf-8")
    with patch("testrail_api_reporter.engines.results_reporter.TestRailAPI"):
        return TestRailResultsReporter(
            url=fake.url(), email=fake.email(), password=fake.password(), project_id=None, xml_report=str(report)
        )


def test_ensure_automation_section_api_failure(reporter):  # pylint: disable=redefined-outer-name
    """A failure fetching sections should be logged and return None"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.sections.get_sections.side_effect = OSError("boom")

    # pylint: disable=protected-access,no-member
    result = reporter._TestRailResultsReporter__ensure_automation_section()

    assert result is None


def test_ensure_automation_section_found_on_first_page(reporter):  # pylint: disable=redefined-outer-name
    """When the section already exists on the first page, its id should be returned without creating one"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.sections.get_sections.return_value = {"sections": [{"id": 7, "name": "pytest"}], "_links": {"next": None}}

    # pylint: disable=protected-access,no-member
    result = reporter._TestRailResultsReporter__ensure_automation_section()

    assert result == 7
    api.sections.add_section.assert_not_called()


def test_ensure_automation_section_found_on_second_page(reporter):  # pylint: disable=redefined-outer-name
    """When the section only exists on a later page, pagination should find it"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    page1 = {"sections": [{"id": 1, "name": "other"}], "_links": {"next": "?page=2&offset=1&limit=1"}}
    page2 = {"sections": [{"id": 8, "name": "pytest"}], "_links": {"next": None}}
    api.sections.get_sections.side_effect = [page1, page2]

    # pylint: disable=protected-access,no-member
    result = reporter._TestRailResultsReporter__ensure_automation_section()

    assert result == 8
    assert api.sections.get_sections.call_count == 2


def test_ensure_automation_section_not_found_creates_new(reporter):  # pylint: disable=redefined-outer-name
    """When no section matches, a new one should be created"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.sections.get_sections.return_value = {"sections": [{"id": 1, "name": "other"}], "_links": {"next": None}}
    api.sections.add_section.return_value = {"id": 99}

    # pylint: disable=protected-access,no-member
    result = reporter._TestRailResultsReporter__ensure_automation_section(title="my_section")

    assert result == 99
    api.sections.add_section.assert_called_once()


def test_ensure_automation_section_create_failure(reporter):  # pylint: disable=redefined-outer-name
    """A failure creating the missing section should be logged and return None"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.sections.get_sections.return_value = {"sections": [], "_links": {"next": None}}
    api.sections.add_section.side_effect = OSError("boom")

    # pylint: disable=protected-access,no-member
    result = reporter._TestRailResultsReporter__ensure_automation_section()

    assert result is None
