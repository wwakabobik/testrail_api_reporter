# -*- coding: utf-8 -*-
"""Tests for content_generator module, update_testrail_case/process_file/process_files methods"""

from unittest.mock import MagicMock, patch

import pytest
from faker import Faker

from testrail_api_reporter.engines.content_generator import (  # pylint: disable=import-error,no-name-in-module
    DEFAULT_FIELD_MAP,
    TestCaseContentGenerator,
)

fake = Faker()


@pytest.fixture
def provider():
    """Fixture to return a mocked AI provider"""
    return MagicMock()


@pytest.fixture
def generator(provider):  # pylint: disable=redefined-outer-name
    """Fixture to return TestCaseContentGenerator with a mocked TestRailAPI and the mocked AI provider"""
    with patch("testrail_api_reporter.engines.content_generator.TestRailAPI"):
        return TestCaseContentGenerator(
            url=fake.url(),
            email=fake.email(),
            password=fake.password(),
            project_id=fake.random_int(),
            provider=provider,
        )


def _content():
    """Build a sample generated-content dict"""
    return {"title": fake.sentence(), "preconditions": fake.sentence(), "steps": fake.sentence()}


def test_update_testrail_case_no_content_skips(generator):  # pylint: disable=redefined-outer-name
    """update_testrail_case should skip (return None) when content is empty, without calling TestRail"""
    api = generator._TestCaseContentGenerator__api  # pylint: disable=protected-access

    result = generator.update_testrail_case("pkg.test_a", {})

    assert result is None
    api.cases.get_cases.assert_not_called()
    api.cases.update_case.assert_not_called()


def test_update_testrail_case_no_matching_case_skips(generator):  # pylint: disable=redefined-outer-name
    """update_testrail_case should skip (return None) when no TestRail case matches the automation_id"""
    api = generator._TestCaseContentGenerator__api  # pylint: disable=protected-access
    api.cases.get_cases.return_value = {"cases": [], "_links": {"next": None}}

    result = generator.update_testrail_case("pkg.test_missing", _content())

    assert result is None
    api.cases.update_case.assert_not_called()


def test_update_testrail_case_updates_matching_case(generator):  # pylint: disable=redefined-outer-name
    """update_testrail_case should map generated fields and call TestRail's update_case for a matching case"""
    api = generator._TestCaseContentGenerator__api  # pylint: disable=protected-access
    api.cases.get_cases.return_value = {
        "cases": [{"id": 42, "custom_automation_id": "pkg.test_a"}],
        "_links": {"next": None},
    }
    content = _content()
    updated_case = {"id": 42}
    api.cases.update_case.return_value = updated_case

    result = generator.update_testrail_case("pkg.test_a", content)

    expected_payload = {DEFAULT_FIELD_MAP[key]: value for key, value in content.items()}
    api.cases.update_case.assert_called_once_with(42, **expected_payload)
    assert result == updated_case


def test_update_testrail_case_custom_field_map(generator):  # pylint: disable=redefined-outer-name
    """update_testrail_case should honour a custom field_map and drop keys not present in it"""
    api = generator._TestCaseContentGenerator__api  # pylint: disable=protected-access
    api.cases.get_cases.return_value = {
        "cases": [{"id": 7, "custom_automation_id": "pkg.test_a"}],
        "_links": {"next": None},
    }
    content = {"title": "My title", "steps": "ignored, not in map"}

    generator.update_testrail_case("pkg.test_a", content, field_map={"title": "title"})

    api.cases.update_case.assert_called_once_with(7, title="My title")


def test_update_testrail_case_api_failure_returns_none(generator):  # pylint: disable=redefined-outer-name
    """update_testrail_case should log and return None if TestRail's update_case raises"""
    api = generator._TestCaseContentGenerator__api  # pylint: disable=protected-access
    api.cases.get_cases.return_value = {
        "cases": [{"id": 42, "custom_automation_id": "pkg.test_a"}],
        "_links": {"next": None},
    }
    api.cases.update_case.side_effect = OSError("boom")

    result = generator.update_testrail_case("pkg.test_a", _content())

    assert result is None


def test_get_all_auto_cases_api_failure_returns_empty(generator):  # pylint: disable=redefined-outer-name
    """A failure fetching the first page of cases should be logged and return {} without caching"""
    api = generator._TestCaseContentGenerator__api  # pylint: disable=protected-access
    api.cases.get_cases.side_effect = OSError("boom")

    # pylint: disable=protected-access,no-member
    result = generator._TestCaseContentGenerator__get_all_auto_cases()

    assert result == {}
    assert generator._TestCaseContentGenerator__cases_by_automation_id == {}  # pylint: disable=protected-access


def test_get_all_auto_cases_multiple_pages(generator):  # pylint: disable=redefined-outer-name
    """Multiple pages of cases should be collected and merged by automation_id"""
    api = generator._TestCaseContentGenerator__api  # pylint: disable=protected-access
    page1 = {
        "cases": [{"id": 1, "custom_automation_id": None}, {"id": 2, "custom_automation_id": "pkg.a"}],
        "_links": {"next": "?page=2&offset=1&limit=1"},
    }
    page2 = {"cases": [{"id": 3, "custom_automation_id": "pkg.b"}], "_links": {"next": None}}
    api.cases.get_cases.side_effect = [page1, page2]

    # pylint: disable=protected-access,no-member
    result = generator._TestCaseContentGenerator__get_all_auto_cases()

    assert result == {"pkg.a": 2, "pkg.b": 3}
    assert api.cases.get_cases.call_count == 2


def test_get_all_auto_cases_is_cached(generator):  # pylint: disable=redefined-outer-name
    """Repeated calls should not re-fetch cases from TestRail once cached"""
    api = generator._TestCaseContentGenerator__api  # pylint: disable=protected-access
    api.cases.get_cases.return_value = {
        "cases": [{"id": 1, "custom_automation_id": "pkg.test_a"}],
        "_links": {"next": None},
    }

    # pylint: disable=protected-access,no-member
    first = generator._TestCaseContentGenerator__get_all_auto_cases()
    second = generator._TestCaseContentGenerator__get_all_auto_cases()

    assert first == second == {"pkg.test_a": 1}
    api.cases.get_cases.assert_called_once()


def test_process_file_dry_run_does_not_update_testrail(
    generator, provider, tmp_path
):  # pylint: disable=redefined-outer-name
    """process_file with dry_run=True should generate content but skip updating TestRail"""
    import json  # pylint: disable=import-outside-toplevel

    file_path = tmp_path / "test_sample.py"
    file_path.write_text("def test_one():\n    assert True\n", encoding="utf-8")
    content = _content()
    provider.generate.return_value = json.dumps(content)
    api = generator._TestCaseContentGenerator__api  # pylint: disable=protected-access

    results = generator.process_file(str(file_path), dry_run=True)

    assert len(results) == 1
    assert results[0]["content"] == content
    assert results[0]["case"] is None
    api.cases.get_cases.assert_not_called()
    api.cases.update_case.assert_not_called()


def test_process_file_updates_testrail(generator, provider, tmp_path):  # pylint: disable=redefined-outer-name
    """process_file should generate content and update the matching TestRail case"""
    import json  # pylint: disable=import-outside-toplevel

    file_path = tmp_path / "test_sample.py"
    file_path.write_text("def test_one():\n    assert True\n", encoding="utf-8")
    content = _content()
    provider.generate.return_value = json.dumps(content)
    api = generator._TestCaseContentGenerator__api  # pylint: disable=protected-access
    automation_id = generator._TestCaseContentGenerator__automation_id(  # pylint: disable=protected-access,no-member
        str(file_path), "test_one"
    )
    api.cases.get_cases.return_value = {
        "cases": [{"id": 99, "custom_automation_id": automation_id}],
        "_links": {"next": None},
    }
    api.cases.update_case.return_value = {"id": 99}

    results = generator.process_file(str(file_path))

    assert results[0]["case"] == {"id": 99}
    assert results[0]["automation_id"] == automation_id


def test_process_files_runs_across_multiple_files(
    generator, provider, tmp_path
):  # pylint: disable=redefined-outer-name
    """process_files should run process_file for each provided file and aggregate the results"""
    import json  # pylint: disable=import-outside-toplevel

    file_one = tmp_path / "test_one.py"
    file_one.write_text("def test_a():\n    assert True\n", encoding="utf-8")
    file_two = tmp_path / "test_two.py"
    file_two.write_text("def test_b():\n    assert True\n", encoding="utf-8")
    provider.generate.side_effect = [json.dumps(_content()), json.dumps(_content())]

    results = generator.process_files([str(file_one), str(file_two)], dry_run=True)

    assert len(results) == 2
    assert {r["automation_id"].split(".")[-1] for r in results} == {"test_a", "test_b"}
