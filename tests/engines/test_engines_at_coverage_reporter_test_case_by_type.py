# -*- coding: utf-8 -*-
"""Tests for at_coverage_reporter module, the ATCoverageReporter class, test_case_by_type method"""

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
            type_platforms=[{"name": "UI", "sections": [1]}],
        )


def test_test_case_by_type_no_project(reporter):  # pylint: disable=redefined-outer-name
    """Call test_case_by_type without a project (none set at init either) should raise ValueError"""
    reporter._ATCoverageReporter__project = None  # pylint: disable=protected-access
    with pytest.raises(ValueError, match="No project specified, report aborted!"):
        reporter.test_case_by_type()


def test_test_case_by_type_no_type_platforms(reporter):  # pylint: disable=redefined-outer-name
    """Call test_case_by_type without type_platforms (none set at init either) should raise ValueError"""
    reporter._ATCoverageReporter__type_platforms = None  # pylint: disable=protected-access
    with pytest.raises(ValueError, match="No platform types are provided, report aborted!"):
        reporter.test_case_by_type()


@patch("testrail_api_reporter.engines.at_coverage_reporter.CSVParser")
def test_test_case_by_type_default_params(mock_csv_parser, reporter):  # pylint: disable=redefined-outer-name
    """Call test_case_by_type with the instance default type_platforms should tally totals per platform"""
    with patch.object(reporter, "_ATCoverageReporter__get_sections", side_effect=lambda sections: sections), patch.object(
        reporter, "_ATCoverageReporter__get_all_cases", return_value=[{}, {}]
    ):
        results = reporter.test_case_by_type()

    assert len(results) == 1
    assert results[0].get_name() == "UI"
    assert results[0].get_total() == 2
    mock_csv_parser.return_value.save_history_data.assert_called_once_with(report=results[0])


@patch("testrail_api_reporter.engines.at_coverage_reporter.CSVParser")
def test_test_case_by_type_custom_params(mock_csv_parser, reporter):  # pylint: disable=redefined-outer-name,unused-argument
    """Call test_case_by_type with explicit type_platforms made of several platforms/sections"""
    type_platforms = [
        {"name": "UI", "sections": [1]},
        {"name": "API", "sections": [2]},
    ]
    with patch.object(
        reporter, "_ATCoverageReporter__get_sections", side_effect=lambda sections: sections + [99]
    ), patch.object(reporter, "_ATCoverageReporter__get_all_cases", return_value=[{}]):
        results = reporter.test_case_by_type(
            project=fake.random_int(), type_platforms=type_platforms, suite=fake.random_int()
        )

    assert [result.get_name() for result in results] == ["UI", "API"]
    for result in results:
        assert result.get_total() == 2  # 2 sections (1 original + 1 appended), 1 case each
