# -*- coding: utf-8 -*-
"""Tests for results_reporter module, the TestRailResultsReporter class, internal __enrich_with_tc_num method"""

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


def test_enrich_with_tc_num_existing_case(reporter):  # pylint: disable=redefined-outer-name
    """A case already known in TestRail (matched by custom_automation_id) should not be re-created"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    xml_dict_list = [{"automation_id": "pkg.test_ok", "time": "0.5", "status": 1, "comment": ""}]
    tc_dict_list = [{"id": 10, "custom_automation_id": "pkg.test_ok"}]

    result = reporter._TestRailResultsReporter__enrich_with_tc_num(  # pylint: disable=protected-access,no-member
        xml_dict_list=xml_dict_list, tc_dict_list=tc_dict_list
    )

    assert result == [{"case_id": 10, "status_id": 1, "comment": "", "elapsed": "0", "attachments": []}]
    api.cases.add_case.assert_not_called()


def test_enrich_with_tc_num_missing_case_created(reporter):  # pylint: disable=redefined-outer-name
    """A case missing in TestRail should be created automatically"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.cases.add_case.return_value = {"id": 55}
    xml_dict_list = [{"automation_id": "pkg.test_new", "time": "1.2", "status": 1, "comment": ""}]

    result = reporter._TestRailResultsReporter__enrich_with_tc_num(  # pylint: disable=protected-access,no-member
        xml_dict_list=xml_dict_list, tc_dict_list=[]
    )

    assert result == [{"case_id": 55, "status_id": 1, "comment": "", "elapsed": "1", "attachments": []}]
    api.cases.add_case.assert_called_once_with(
        section_id=reporter._TestRailResultsReporter__at_section,  # pylint: disable=protected-access
        title="pkg.test_new",
        custom_automation_id="pkg.test_new",
    )


def test_enrich_with_tc_num_missing_case_creation_failure(reporter):  # pylint: disable=redefined-outer-name
    """A failure creating a missing case should be logged and return None"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.cases.add_case.side_effect = OSError("boom")
    xml_dict_list = [{"automation_id": "pkg.test_new", "time": "1.2", "status": 1, "comment": ""}]

    result = reporter._TestRailResultsReporter__enrich_with_tc_num(  # pylint: disable=protected-access,no-member
        xml_dict_list=xml_dict_list, tc_dict_list=[]
    )

    assert result is None


def test_enrich_with_tc_num_item_with_failure_key(reporter):  # pylint: disable=redefined-outer-name
    """An item carrying a 'failure' key should use its 'message' field as the comment"""
    tc_dict_list = [{"id": 10, "custom_automation_id": "pkg.test_failed"}]
    xml_dict_list = [{"automation_id": "pkg.test_failed", "time": "0.1", "status": 5, "failure": {}, "message": "boom"}]

    result = reporter._TestRailResultsReporter__enrich_with_tc_num(  # pylint: disable=protected-access,no-member
        xml_dict_list=xml_dict_list, tc_dict_list=tc_dict_list
    )

    assert result[0]["comment"] == "boom"
