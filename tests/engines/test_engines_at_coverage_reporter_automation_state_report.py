# -*- coding: utf-8 -*-
"""Tests for at_coverage_reporter module, the ATCoverageReporter class, automation_state_report method"""

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
            url=fake.url(),
            email=fake.email(),
            password=fake.password(),
            project=fake.random_int(),
            priority=[4],
            automation_platforms=[
                {"name": "Desktop", "sections": [1], "internal_name": "type_id", "auto_code": 3, "na_code": 4}
            ],
        )


def test_automation_state_report_no_project(reporter):  # pylint: disable=redefined-outer-name
    """Call automation_state_report without a project (none set at init either) should raise ValueError"""
    reporter._ATCoverageReporter__project = None  # pylint: disable=protected-access
    with pytest.raises(ValueError, match="No project specified, report aborted!"):
        reporter.automation_state_report()


def test_automation_state_report_no_priority(reporter):  # pylint: disable=redefined-outer-name
    """Call automation_state_report without priority (none set at init either) should raise ValueError"""
    reporter._ATCoverageReporter__priority = None  # pylint: disable=protected-access
    with pytest.raises(ValueError, match="No critical priority specified, report aborted!"):
        reporter.automation_state_report()


def test_automation_state_report_no_automation_platforms(reporter):  # pylint: disable=redefined-outer-name
    """Call automation_state_report without automation_platforms (none set at init either) should raise ValueError"""
    reporter._ATCoverageReporter__automation_platforms = None  # pylint: disable=protected-access
    with pytest.raises(ValueError, match="No automation platforms specified, report aborted!"):
        reporter.automation_state_report()


@patch("testrail_api_reporter.engines.at_coverage_reporter.CSVParser")
def test_automation_state_report_success(mock_csv_parser, reporter):  # pylint: disable=redefined-outer-name
    """A full run should tally automated, not applicable and not automated cases per platform"""
    automation_platforms = [
        {"name": "Desktop", "sections": [1], "internal_name": "type_id", "auto_code": 3, "na_code": 4},
        {"name": "Mobile", "sections": [2], "internal_name": "type_id", "auto_code": 3, "na_code": 4},
    ]
    cases = [{"type_id": 3}, {"type_id": 4}, {"type_id": 1}]  # 1 automated, 1 n/a, 1 neither (not automated)

    with patch.object(
        reporter, "_ATCoverageReporter__get_sections", side_effect=lambda sections: sections
    ), patch.object(reporter, "_ATCoverageReporter__get_all_cases", return_value=cases):
        results = reporter.automation_state_report(automation_platforms=automation_platforms)

    assert len(results) == 2
    for result in results:
        assert result.get_total() == len(cases)
        assert result.get_automated() == 1
        assert result.get_not_applicable() == 1
        assert result.get_not_automated() == 1
    assert mock_csv_parser.return_value.save_history_data.call_count == 2
