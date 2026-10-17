# -*- coding: utf-8 -*-
"""Tests for results_reporter module, the TestRailResultsReporter class, internal __xml_to_dict method"""

from unittest.mock import patch

import pytest
from faker import Faker

from testrail_api_reporter.engines.results_reporter import (  # pylint: disable=import-error,no-name-in-module
    TestRailResultsReporter,
)

fake = Faker()


def _single_testcase_xml(testcase_xml):
    """Wrap a single <testcase> block into a full junit testsuites document"""
    return (
        '<testsuites><testsuite timestamp="2024-01-01T10:00:00.123456">' f"{testcase_xml}" "</testsuite></testsuites>"
    )


def _multi_testcase_xml(*testcase_blocks):
    """Wrap multiple <testcase> blocks into a full junit testsuites document"""
    return (
        '<testsuites><testsuite timestamp="2024-01-01T10:00:00.123456">'
        f"{''.join(testcase_blocks)}"
        "</testsuite></testsuites>"
    )


@pytest.fixture
def reporter(tmp_path):
    """Fixture to return TestRailResultsReporter with a mocked TestRailAPI and a valid (empty) xml report"""
    report = tmp_path / "junit-report.xml"
    report.write_text("<testsuites></testsuites>", encoding="utf-8")
    with patch("testrail_api_reporter.engines.results_reporter.TestRailAPI"):
        return TestRailResultsReporter(
            url=fake.url(), email=fake.email(), password=fake.password(), project_id=None, xml_report=str(report)
        )


def test_xml_to_dict_report_missing(reporter):  # pylint: disable=redefined-outer-name
    """When the xml report no longer exists, __xml_to_dict should return None"""
    reporter._TestRailResultsReporter__xml_report = None  # pylint: disable=protected-access

    result = reporter._TestRailResultsReporter__xml_to_dict()  # pylint: disable=protected-access,no-member

    assert result is None


def test_xml_to_dict_single_passed_case(reporter, tmp_path):  # pylint: disable=redefined-outer-name
    """A single passing test case (not wrapped in a list by xmltodict) should be parsed correctly"""
    report = tmp_path / "single.xml"
    report.write_text(
        _single_testcase_xml('<testcase classname="pkg.mod" name="test_ok" time="0.1"></testcase>'),
        encoding="utf-8",
    )
    reporter._TestRailResultsReporter__xml_report = str(report)  # pylint: disable=protected-access

    # pylint: disable=protected-access,no-member
    result = reporter._TestRailResultsReporter__xml_to_dict(filename=str(report))

    assert result == [{"automation_id": "pkg.mod.test_ok", "time": "0.1", "status": 1, "comment": ""}]


def test_xml_to_dict_multiple_cases_all_statuses(reporter, tmp_path):  # pylint: disable=redefined-outer-name
    """Failure, skipped-xfail, skipped-other and passing cases should each map to the right status"""
    report = tmp_path / "multi.xml"
    report.write_text(
        _multi_testcase_xml(
            '<testcase classname="pkg" name="test_failed" time="0.1">'
            '<failure message="boom">traceback</failure></testcase>',
            '<testcase classname="pkg" name="test_xfail" time="0.2">'
            '<skipped type="pytest.xfail" message="expected"/></testcase>',
            '<testcase classname="pkg" name="test_skipped" time="0.3">'
            '<skipped type="pytest.skip" message="skip me"/></testcase>',
            '<testcase classname="pkg" name="test_ok" time="0.4"></testcase>',
        ),
        encoding="utf-8",
    )
    reporter._TestRailResultsReporter__xml_report = str(report)  # pylint: disable=protected-access

    # pylint: disable=protected-access,no-member
    result = reporter._TestRailResultsReporter__xml_to_dict(filename=str(report))

    statuses = {item["automation_id"]: item["status"] for item in result}
    assert statuses == {
        "pkg.test_failed": 5,
        "pkg.test_xfail": 5,
        "pkg.test_skipped": 7,
        "pkg.test_ok": 1,
    }
    failed = next(item for item in result if item["automation_id"] == "pkg.test_failed")
    assert failed["comment"] == "boom : traceback"
    passed = next(item for item in result if item["automation_id"] == "pkg.test_ok")
    assert passed["comment"] == ""
