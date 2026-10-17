# -*- coding: utf-8 -*-
"""Tests for results_reporter module, the TestRailResultsReporter class, internal __resolve_skipped_status_id
method and its effect on __xml_to_dict status mapping for non-xfail skipped tests"""

from unittest.mock import patch

import pytest
from faker import Faker

from testrail_api_reporter.engines.results_reporter import (  # pylint: disable=import-error,no-name-in-module
    DEFAULT_SKIPPED_STATUS_ID,
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


def test_resolve_skipped_status_id_matches_by_label(reporter):  # pylint: disable=redefined-outer-name
    """A status whose 'label' matches skipped_status_name should be used"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.statuses.get_statuses.return_value = [
        {"id": 1, "name": "passed", "label": "Passed"},
        {"id": 9, "name": "custom_status4", "label": "Skipped"},
    ]

    # pylint: disable=protected-access,no-member
    result = reporter._TestRailResultsReporter__resolve_skipped_status_id()

    assert result == 9


def test_resolve_skipped_status_id_matches_by_name(reporter):  # pylint: disable=redefined-outer-name
    """A status whose 'name' matches skipped_status_name should also be used"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.statuses.get_statuses.return_value = [{"id": 11, "name": "Skipped", "label": "Custom label"}]

    # pylint: disable=protected-access,no-member
    result = reporter._TestRailResultsReporter__resolve_skipped_status_id()

    assert result == 11


def test_resolve_skipped_status_id_no_match_falls_back(reporter):  # pylint: disable=redefined-outer-name
    """When no status matches, the default id should be used"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.statuses.get_statuses.return_value = [{"id": 1, "name": "passed", "label": "Passed"}]

    # pylint: disable=protected-access,no-member
    result = reporter._TestRailResultsReporter__resolve_skipped_status_id()

    assert result == DEFAULT_SKIPPED_STATUS_ID


def test_resolve_skipped_status_id_api_failure_falls_back(reporter):  # pylint: disable=redefined-outer-name
    """When fetching statuses fails, the default id should be used"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.statuses.get_statuses.side_effect = OSError("boom")

    # pylint: disable=protected-access,no-member
    result = reporter._TestRailResultsReporter__resolve_skipped_status_id()

    assert result == DEFAULT_SKIPPED_STATUS_ID


def test_resolve_skipped_status_id_caches_result(reporter):  # pylint: disable=redefined-outer-name
    """The resolved status id should be cached, so get_statuses is only called once"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.statuses.get_statuses.return_value = [{"id": 9, "name": "custom_status4", "label": "Skipped"}]

    # pylint: disable=protected-access,no-member
    first = reporter._TestRailResultsReporter__resolve_skipped_status_id()
    second = reporter._TestRailResultsReporter__resolve_skipped_status_id()

    assert first == second == 9
    api.statuses.get_statuses.assert_called_once()


def test_xml_to_dict_skipped_uses_resolved_status(reporter, tmp_path):  # pylint: disable=redefined-outer-name
    """A non-xfail skipped test case should be mapped to the resolved (not hardcoded) status id"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.statuses.get_statuses.return_value = [{"id": 42, "name": "custom_status9", "label": "Skipped"}]
    report = tmp_path / "skipped.xml"
    report.write_text(
        '<testsuites><testsuite timestamp="2024-01-01T10:00:00.123456">'
        '<testcase classname="pkg" name="test_skipped" time="0.1">'
        '<skipped type="pytest.skip" message="skip me"/></testcase>'
        "</testsuite></testsuites>",
        encoding="utf-8",
    )
    reporter._TestRailResultsReporter__xml_report = str(report)  # pylint: disable=protected-access

    # pylint: disable=protected-access,no-member
    result = reporter._TestRailResultsReporter__xml_to_dict(filename=str(report))

    assert result == [{"automation_id": "pkg.test_skipped", "time": "0.1", "status": 42, "comment": ""}]
