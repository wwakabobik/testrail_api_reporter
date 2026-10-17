# -*- coding: utf-8 -*-
"""Tests for results_reporter module, the TestRailResultsReporter class, internal __prepare_payload
and __prepare_title methods"""

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


def test_prepare_payload_no_parsed_xml(reporter):  # pylint: disable=redefined-outer-name
    """When the xml report could not be parsed, __prepare_payload should return None"""
    with patch.object(reporter, "_TestRailResultsReporter__xml_to_dict", return_value=None), patch.object(
        reporter, "_TestRailResultsReporter__get_all_auto_cases", return_value=[]
    ):
        result = reporter._TestRailResultsReporter__prepare_payload()  # pylint: disable=protected-access,no-member

    assert result is None


def test_prepare_payload_success(reporter):  # pylint: disable=redefined-outer-name
    """When the xml report is parsed, __prepare_payload should delegate enrichment and return its result"""
    parsed_xml = [{"automation_id": "pkg.test_ok"}]
    parsed_cases = [{"id": 1}]
    enriched = [{"case_id": 1}]
    with patch.object(
        reporter, "_TestRailResultsReporter__xml_to_dict", return_value=parsed_xml
    ) as mock_xml_to_dict, patch.object(
        reporter, "_TestRailResultsReporter__get_all_auto_cases", return_value=parsed_cases
    ), patch.object(
        reporter, "_TestRailResultsReporter__enrich_with_tc_num", return_value=enriched
    ) as mock_enrich:
        result = reporter._TestRailResultsReporter__prepare_payload()  # pylint: disable=protected-access,no-member

    assert result == enriched
    mock_xml_to_dict.assert_called_once()
    mock_enrich.assert_called_once_with(xml_dict_list=parsed_xml, tc_dict_list=parsed_cases)


def test_prepare_title_default(reporter):  # pylint: disable=redefined-outer-name
    """With no environment and no timestamp, the title should use the instance timestamp"""
    reporter._TestRailResultsReporter__timestamp = "2024-01-01T10:00:00"  # pylint: disable=protected-access

    result = reporter._TestRailResultsReporter__prepare_title()  # pylint: disable=protected-access,no-member

    assert result == "AT run 2024-01-01T10:00:00"


def test_prepare_title_custom_timestamp_and_environment(reporter):  # pylint: disable=redefined-outer-name
    """With an explicit timestamp and environment, both should be reflected in the title"""
    timestamp = fake.date()
    environment = fake.word()

    result = reporter._TestRailResultsReporter__prepare_title(  # pylint: disable=protected-access,no-member
        environment=environment, timestamp=timestamp
    )

    assert result == f"AT run {timestamp} on {environment}"
