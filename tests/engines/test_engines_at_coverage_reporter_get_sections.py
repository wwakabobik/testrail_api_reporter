# -*- coding: utf-8 -*-
"""Tests for at_coverage_reporter module, the ATCoverageReporter class, internal __get_sections method"""

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


def test_get_sections_no_project(reporter):  # pylint: disable=redefined-outer-name
    """Call __get_sections without a project (none set at init either) should raise ValueError"""
    reporter._ATCoverageReporter__project = None  # pylint: disable=protected-access
    with pytest.raises(ValueError, match="No project specified, report aborted!"):
        reporter._ATCoverageReporter__get_sections([1])  # pylint: disable=protected-access,no-member


def test_get_sections_collects_matching_children(reporter):  # pylint: disable=redefined-outer-name
    """Sections whose parent_id is already known should be appended; others should be skipped"""
    all_sections = [
        {"id": 2, "parent_id": 1},  # matches parent_list, appended
        {"id": 3, "parent_id": 999},  # does not match, skipped
    ]
    with patch.object(reporter, "_ATCoverageReporter__get_all_sections", return_value=all_sections):
        result = reporter._ATCoverageReporter__get_sections([1])  # pylint: disable=protected-access,no-member

    assert result == [1, 2]
