# -*- coding: utf-8 -*-
"""Live tests for ATCoverageReporter against a real TestRail instance"""

from os import getenv

import pytest

from testrail_api_reporter.engines.at_coverage_reporter import (  # pylint: disable=import-error,no-name-in-module
    ATCoverageReporter,
)

requires_live_testrail = pytest.mark.skipif(
    not (
        getenv("TESTRAIL_URL")
        and getenv("TESTRAIL_EMAIL")
        and getenv("TESTRAIL_PASSWORD")
        and getenv("TESTRAIL_PROJECT_ID")
    ),
    reason="Live TestRail tests require TESTRAIL_URL, TESTRAIL_EMAIL, TESTRAIL_PASSWORD and TESTRAIL_PROJECT_ID",
)


@requires_live_testrail
def test_test_case_by_priority_returns_counts_for_all_priorities(
    tr_url, tr_email, tr_password, tr_project_id, tr_suite_id
):
    """test_case_by_priority should return one non-negative count per priority (1-4), proving pagination works"""
    reporter = ATCoverageReporter(
        url=tr_url, email=tr_email, password=tr_password, project=tr_project_id, suite_id=tr_suite_id
    )

    result = reporter.test_case_by_priority(project=tr_project_id, suite=tr_suite_id)

    assert len(result) == 4
    assert all(isinstance(count, int) and count >= 0 for count in result)
