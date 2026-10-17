# -*- coding: utf-8 -*-
"""Tests for results_reporter module, the TestRailResultsReporter class, setters and internal __check_* methods"""

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


# --- set_project_id ---


def test_set_project_id_success(reporter):  # pylint: disable=redefined-outer-name
    """A valid project id should be stored"""
    project_id = fake.random_int()
    reporter.set_project_id(project_id)
    assert reporter._TestRailResultsReporter__project_id == project_id  # pylint: disable=protected-access


def test_set_project_id_failure(reporter):  # pylint: disable=redefined-outer-name
    """An invalid project id should be stored as None"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.projects.get_project.side_effect = OSError("boom")
    reporter.set_project_id(fake.random_int())
    assert reporter._TestRailResultsReporter__project_id is None  # pylint: disable=protected-access


# --- set_suite_id ---


def test_set_suite_id_success(reporter):  # pylint: disable=redefined-outer-name
    """A valid suite id should be stored when the project check passes"""
    suite_id = fake.random_int()
    reporter.set_suite_id(suite_id)
    assert reporter._TestRailResultsReporter__suite_id == suite_id  # pylint: disable=protected-access


def test_set_suite_id_invalid_suite(reporter):  # pylint: disable=redefined-outer-name
    """An invalid suite id should be stored as None when the project check passes"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.suites.get_suite.side_effect = OSError("boom")
    reporter.set_suite_id(fake.random_int())
    assert reporter._TestRailResultsReporter__suite_id is None  # pylint: disable=protected-access


def test_set_suite_id_project_check_fails(reporter):  # pylint: disable=redefined-outer-name
    """When the project check fails, the suite id should not even be looked at"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.projects.get_project.side_effect = OSError("boom")
    api.suites.get_suite.reset_mock()  # clear the call already made during __init__
    reporter.set_suite_id(fake.random_int())
    api.suites.get_suite.assert_not_called()


# --- set_xml_filename ---


def test_set_xml_filename_success(reporter, tmp_path):  # pylint: disable=redefined-outer-name
    """An existing xml filename should be stored"""
    new_report = tmp_path / "other.xml"
    new_report.write_text("<testsuites></testsuites>", encoding="utf-8")
    reporter.set_xml_filename(str(new_report))
    assert reporter._TestRailResultsReporter__xml_report == str(new_report)  # pylint: disable=protected-access


def test_set_xml_filename_missing(reporter):  # pylint: disable=redefined-outer-name
    """A non-existent xml filename should be stored as None"""
    reporter.set_xml_filename(fake.file_name(extension="xml"))
    assert reporter._TestRailResultsReporter__xml_report is None  # pylint: disable=protected-access


# --- set_at_report_section ---


def test_set_at_report_section_success(reporter):  # pylint: disable=redefined-outer-name
    """When both project and suite checks pass, the automation section should be (re)resolved"""
    with patch.object(reporter, "_TestRailResultsReporter__ensure_automation_section", return_value=123) as mock_ensure:
        reporter.set_at_report_section("my_section")

    mock_ensure.assert_called_once_with(title="my_section")
    assert reporter._TestRailResultsReporter__at_section == 123  # pylint: disable=protected-access


def test_set_at_report_section_project_check_fails(reporter):  # pylint: disable=redefined-outer-name
    """When the project check fails, the automation section should not be looked up"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.projects.get_project.side_effect = OSError("boom")
    with patch.object(reporter, "_TestRailResultsReporter__ensure_automation_section") as mock_ensure:
        reporter.set_at_report_section("my_section")

    mock_ensure.assert_not_called()


def test_set_at_report_section_suite_check_fails(reporter):  # pylint: disable=redefined-outer-name
    """When the suite check fails, the automation section should not be looked up"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.suites.get_suite.side_effect = OSError("boom")
    with patch.object(reporter, "_TestRailResultsReporter__ensure_automation_section") as mock_ensure:
        reporter.set_at_report_section("my_section")

    mock_ensure.assert_not_called()


# --- set_timestamp ---


def test_set_timestamp(reporter):  # pylint: disable=redefined-outer-name
    """The timestamp should be stored as given"""
    new_timestamp = fake.date()
    reporter.set_timestamp(new_timestamp)
    assert reporter._TestRailResultsReporter__timestamp == new_timestamp  # pylint: disable=protected-access


# --- __check_section / __check_run_exists ---


def test_check_section_success(reporter):  # pylint: disable=redefined-outer-name
    """A valid section id should return True"""
    # pylint: disable=protected-access,no-member
    assert reporter._TestRailResultsReporter__check_section(section_id=fake.random_int()) is True


def test_check_section_failure(reporter):  # pylint: disable=redefined-outer-name
    """An invalid section id should return False"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.sections.get_section.side_effect = OSError("boom")
    assert reporter._TestRailResultsReporter__check_section() is False  # pylint: disable=protected-access,no-member


def test_check_run_exists_success(reporter):  # pylint: disable=redefined-outer-name
    """An existing run id should return True"""
    # pylint: disable=protected-access,no-member
    assert reporter._TestRailResultsReporter__check_run_exists(run_id=fake.random_int()) is True


def test_check_run_exists_failure(reporter):  # pylint: disable=redefined-outer-name
    """A non-existent run id should return False"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.runs.get_run.side_effect = OSError("boom")
    assert reporter._TestRailResultsReporter__check_run_exists() is False  # pylint: disable=protected-access,no-member


# --- __check_report_exists ---


def test_check_report_exists_explicit_existing(reporter, tmp_path):  # pylint: disable=redefined-outer-name
    """An explicit, existing report path should return True"""
    report = tmp_path / "explicit.xml"
    report.write_text("<testsuites></testsuites>", encoding="utf-8")
    # pylint: disable=protected-access,no-member
    assert reporter._TestRailResultsReporter__check_report_exists(xml_report=str(report)) is True


def test_check_report_exists_falls_back_to_instance(reporter):  # pylint: disable=redefined-outer-name
    """With no explicit path, the instance's own xml_report should be used"""
    # pylint: disable=protected-access,no-member
    assert reporter._TestRailResultsReporter__check_report_exists() is True


def test_check_report_exists_missing(reporter):  # pylint: disable=redefined-outer-name
    """A non-existent report path should return False"""
    result = reporter._TestRailResultsReporter__check_report_exists(  # pylint: disable=protected-access,no-member
        xml_report=fake.file_name(extension="xml")
    )
    assert result is False


def test_check_report_exists_no_path_at_all(reporter):  # pylint: disable=redefined-outer-name
    """With neither an explicit nor an instance path, it should return False"""
    reporter._TestRailResultsReporter__xml_report = None  # pylint: disable=protected-access
    # pylint: disable=protected-access,no-member
    assert reporter._TestRailResultsReporter__check_report_exists() is False


# --- __self_check ---


def test_self_check_calls_every_check(reporter):  # pylint: disable=redefined-outer-name
    """__self_check should call every individual check once"""
    with patch.object(reporter, "_TestRailResultsReporter__check_project") as mock_project, patch.object(
        reporter, "_TestRailResultsReporter__check_suite"
    ) as mock_suite, patch.object(reporter, "_TestRailResultsReporter__check_section") as mock_section, patch.object(
        reporter, "_TestRailResultsReporter__check_report_exists"
    ) as mock_report:
        reporter._TestRailResultsReporter__self_check()  # pylint: disable=protected-access,no-member

    mock_project.assert_called_once()
    mock_suite.assert_called_once()
    mock_section.assert_called_once()
    mock_report.assert_called_once()
