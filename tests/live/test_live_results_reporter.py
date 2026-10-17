# -*- coding: utf-8 -*-
"""Live tests for TestRailResultsReporter against a real TestRail instance"""

from os import getenv
from uuid import uuid4

import pytest

from testrail_api_reporter.engines.results_reporter import (  # pylint: disable=import-error,no-name-in-module
    TestRailResultsReporter,
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
def test_init_connects_and_prepares_automation_section(
    tr_url, tr_email, tr_password, tr_project_id, tr_suite_id, tmp_path
):  # pylint: disable=too-many-arguments
    """Construction should validate project/suite against the live instance and ensure the pytest section"""
    report = tmp_path / "junit-report.xml"
    report.write_text("<testsuites></testsuites>", encoding="utf-8")

    reporter = TestRailResultsReporter(
        url=tr_url,
        email=tr_email,
        password=tr_password,
        project_id=tr_project_id,
        xml_report=str(report),
        suite_id=tr_suite_id,
    )

    # pylint: disable=protected-access,no-member
    assert reporter._TestRailResultsReporter__project_id == tr_project_id
    assert reporter._TestRailResultsReporter__at_section is not None


@requires_live_testrail
def test_send_results_round_trip(
    tr_url, tr_email, tr_password, tr_project_id, tr_suite_id, tr_api, tmp_path
):  # pylint: disable=too-many-arguments,too-many-locals
    """send_results should create a run, auto-create matching cases, submit results and close the run"""
    unique = uuid4().hex[:8]
    report = tmp_path / "junit-report.xml"
    report.write_text(
        '<testsuites><testsuite timestamp="2024-01-01T10:00:00.000000">'
        f'<testcase classname="live.{unique}" name="test_pass" time="0.1"></testcase>'
        f'<testcase classname="live.{unique}" name="test_fail" time="0.2">'
        '<failure message="boom">traceback</failure></testcase>'
        "</testsuite></testsuites>",
        encoding="utf-8",
    )
    run_name = f"live-test-run-{unique}"

    reporter = TestRailResultsReporter(
        url=tr_url,
        email=tr_email,
        password=tr_password,
        project_id=tr_project_id,
        xml_report=str(report),
        suite_id=tr_suite_id,
    )

    run_id = None
    case_ids: list = []
    try:
        run_id = reporter.send_results(run_name=run_name, close_run=True)
        assert isinstance(run_id, int)

        run = tr_api.runs.get_run(run_id=run_id)
        assert run["name"] == run_name
        assert run["is_completed"] is True

        tests_in_run = tr_api.tests.get_tests(run_id=run_id)["tests"]
        case_ids = [test["case_id"] for test in tests_in_run]
        assert len(case_ids) == 2

        results = tr_api.results.get_results_for_run(run_id=run_id)["results"]
        assert len(results) == 2
        assert {result["status_id"] for result in results} == {1, 5}
    finally:
        if run_id:
            tr_api.runs.delete_run(run_id=run_id)
        for case_id in case_ids:
            tr_api.cases.delete_case(case_id=case_id)
