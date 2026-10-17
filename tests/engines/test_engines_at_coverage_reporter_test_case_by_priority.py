# -*- coding: utf-8 -*-
"""Tests for at_coverage_reporter module, the ATCoverageReporter class, test_case_by_priority method"""

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
        return ATCoverageReporter(url=fake.url(), email=fake.email(), password=fake.password(), project=fake.random_int())


def test_test_case_by_priority_no_project(reporter):  # pylint: disable=redefined-outer-name
    """Call test_case_by_priority without a project (none set at init either) should raise ValueError"""
    reporter._ATCoverageReporter__project = None  # pylint: disable=protected-access
    with pytest.raises(ValueError, match="No project specified, report aborted!"):
        reporter.test_case_by_priority()


def test_test_case_by_priority_default_params(reporter):  # pylint: disable=redefined-outer-name
    """Call test_case_by_priority with the instance default project should return 4 priority counts"""
    with patch.object(reporter, "_ATCoverageReporter__get_all_cases", return_value=[{}, {}]) as mock_get_all_cases:
        result = reporter.test_case_by_priority()

    assert result == [2, 2, 2, 2]
    assert mock_get_all_cases.call_count == 4


def test_test_case_by_priority_custom_params(reporter):  # pylint: disable=redefined-outer-name
    """Call test_case_by_priority with explicit project/suite should pass them through"""
    project = fake.random_int()
    suite = fake.random_int()
    with patch.object(reporter, "_ATCoverageReporter__get_all_cases", return_value=[{}]) as mock_get_all_cases:
        result = reporter.test_case_by_priority(project=project, suite=suite)

    assert result == [1, 1, 1, 1]
    mock_get_all_cases.assert_any_call(project_id=project, suite_id=suite, priority_id="1")
