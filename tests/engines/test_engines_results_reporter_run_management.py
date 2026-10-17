# -*- coding: utf-8 -*-
"""Tests for results_reporter module, the TestRailResultsReporter class, internal run management methods:
__search_for_run_by_name, __delete_run, __add_run, __add_results, __prepare_runs, __close_run"""

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


# --- __search_for_run_by_name ---


def test_search_for_run_by_name_api_failure(reporter):  # pylint: disable=redefined-outer-name
    """A failure listing runs should be logged and return None"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.runs.get_runs.side_effect = OSError("boom")

    result = reporter._TestRailResultsReporter__search_for_run_by_name(title=fake.sentence())  # pylint: disable=protected-access,no-member

    assert result is None


def test_search_for_run_by_name_found_first_page(reporter):  # pylint: disable=redefined-outer-name
    """A run matching the title on the first page should be returned"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    title = fake.sentence()
    api.runs.get_runs.return_value = {"runs": {"name": title, "id": 77}, "_links": {"next": None}}

    result = reporter._TestRailResultsReporter__search_for_run_by_name(title=title)  # pylint: disable=protected-access,no-member

    assert result == 77


def test_search_for_run_by_name_not_found(reporter):  # pylint: disable=redefined-outer-name
    """When no run matches the title, None should be returned"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.runs.get_runs.return_value = {"runs": {"name": fake.sentence(), "id": 1}, "_links": {"next": None}}

    result = reporter._TestRailResultsReporter__search_for_run_by_name(title=fake.sentence())  # pylint: disable=protected-access,no-member

    assert result is None


def test_search_for_run_by_name_pagination_crashes(reporter):  # pylint: disable=redefined-outer-name
    """`response` is reset to None at the top of every loop iteration, so once the first page says there is a
    next page, the pagination branch dereferences that None and crashes (pre-existing behaviour)"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    page1 = {"runs": {"name": fake.sentence(), "id": 1}, "_links": {"next": "?page=2&offset=1&limit=1"}}
    api.runs.get_runs.return_value = page1

    with pytest.raises(TypeError):
        reporter._TestRailResultsReporter__search_for_run_by_name(title=fake.sentence())  # pylint: disable=protected-access,no-member


# --- __delete_run ---


def test_delete_run_success(reporter):  # pylint: disable=redefined-outer-name
    """A successful deletion should return True"""
    assert reporter._TestRailResultsReporter__delete_run(run_id=fake.random_int()) is True  # pylint: disable=protected-access,no-member


def test_delete_run_failure(reporter):  # pylint: disable=redefined-outer-name
    """A failed deletion should be logged and return False"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.runs.delete_run.side_effect = OSError("boom")

    assert reporter._TestRailResultsReporter__delete_run() is False  # pylint: disable=protected-access,no-member


# --- __add_run ---


def test_add_run_success(reporter):  # pylint: disable=redefined-outer-name
    """A successful run creation should return the new run id"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.runs.add_run.return_value = {"id": 42}

    result = reporter._TestRailResultsReporter__add_run(title=fake.sentence(), cases_list=[1, 2])  # pylint: disable=protected-access,no-member

    assert result == 42


def test_add_run_failure(reporter):  # pylint: disable=redefined-outer-name
    """A failed run creation should be logged, self-checked and return None"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.runs.add_run.side_effect = OSError("boom")

    with patch.object(reporter, "_TestRailResultsReporter__self_check") as mock_self_check:
        result = reporter._TestRailResultsReporter__add_run(title=fake.sentence())  # pylint: disable=protected-access,no-member

    assert result is None
    mock_self_check.assert_called_once()


# --- __add_results ---


def test_add_results_success(reporter):  # pylint: disable=redefined-outer-name
    """A successful submission should return the run id"""
    run_id = fake.random_int()

    result = reporter._TestRailResultsReporter__add_results(run_id=run_id, results=[{"case_id": 1}])  # pylint: disable=protected-access,no-member

    assert result == run_id


def test_add_results_failure(reporter):  # pylint: disable=redefined-outer-name
    """A failed submission should be logged, self-checked, have its run existence checked and return False"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.results.add_results_for_cases.side_effect = OSError("boom")

    with patch.object(reporter, "_TestRailResultsReporter__self_check") as mock_self_check:
        result = reporter._TestRailResultsReporter__add_results(run_id=fake.random_int(), results=[])  # pylint: disable=protected-access,no-member

    assert result is False
    mock_self_check.assert_called_once()
    api.runs.get_run.assert_called_once()


# --- __prepare_runs ---


def test_prepare_runs_no_run_name_creates_new(reporter):  # pylint: disable=redefined-outer-name
    """With no run_name, a new run should always be created"""
    with patch.object(reporter, "_TestRailResultsReporter__add_run", return_value=99) as mock_add_run:
        result = reporter._TestRailResultsReporter__prepare_runs(  # pylint: disable=protected-access,no-member
            cases=[{"case_id": 1}, {"case_id": 2}], title=fake.sentence()
        )

    assert result == 99
    mock_add_run.assert_called_once_with(title=mock_add_run.call_args.kwargs["title"], cases_list=[1, 2], include_all=False)


def test_prepare_runs_run_name_not_found_creates_new(reporter):  # pylint: disable=redefined-outer-name
    """With a run_name that matches no existing run, a new run should be created"""
    with patch.object(
        reporter, "_TestRailResultsReporter__search_for_run_by_name", return_value=None
    ), patch.object(reporter, "_TestRailResultsReporter__add_run", return_value=99) as mock_add_run:
        result = reporter._TestRailResultsReporter__prepare_runs(  # pylint: disable=protected-access,no-member
            cases=[{"case_id": 1}], title=fake.sentence(), run_name=fake.sentence()
        )

    assert result == 99
    mock_add_run.assert_called_once()


def test_prepare_runs_run_name_found_reused(reporter):  # pylint: disable=redefined-outer-name
    """With a run_name that matches an existing run (and no deletion requested), that run should be reused"""
    with patch.object(
        reporter, "_TestRailResultsReporter__search_for_run_by_name", return_value=55
    ), patch.object(reporter, "_TestRailResultsReporter__add_run") as mock_add_run:
        result = reporter._TestRailResultsReporter__prepare_runs(  # pylint: disable=protected-access,no-member
            cases=[{"case_id": 1}], title=fake.sentence(), run_name=fake.sentence()
        )

    assert result == 55
    mock_add_run.assert_not_called()


def test_prepare_runs_run_name_found_deleted_and_recreated(reporter):  # pylint: disable=redefined-outer-name
    """With delete_run requested and an existing run found, it should be deleted and a new one created"""
    with patch.object(
        reporter, "_TestRailResultsReporter__search_for_run_by_name", return_value=55
    ), patch.object(reporter, "_TestRailResultsReporter__delete_run") as mock_delete_run, patch.object(
        reporter, "_TestRailResultsReporter__add_run", return_value=99
    ) as mock_add_run:
        result = reporter._TestRailResultsReporter__prepare_runs(  # pylint: disable=protected-access,no-member
            cases=[{"case_id": 1}], title=fake.sentence(), run_name=fake.sentence(), delete_run=True
        )

    assert result == 99
    mock_delete_run.assert_called_once_with(run_id=55)
    mock_add_run.assert_called_once()


def test_prepare_runs_existing_run_id_no_run_name(reporter):  # pylint: disable=redefined-outer-name
    """An explicit run_id with no run_name and no deletion should be reused as-is"""
    run_id = fake.random_int()
    with patch.object(reporter, "_TestRailResultsReporter__add_run") as mock_add_run:
        result = reporter._TestRailResultsReporter__prepare_runs(  # pylint: disable=protected-access,no-member
            cases=[{"case_id": 1}], title=fake.sentence(), run_id=run_id
        )

    assert result == run_id
    mock_add_run.assert_not_called()


# --- __close_run ---


def test_close_run_success(reporter):  # pylint: disable=redefined-outer-name
    """A successful close should return True"""
    assert reporter._TestRailResultsReporter__close_run(run_id=fake.random_int(), title=fake.sentence()) is True  # pylint: disable=protected-access,no-member


def test_close_run_failure(reporter):  # pylint: disable=redefined-outer-name
    """A failed close should be logged and return False"""
    api = reporter._TestRailResultsReporter__api  # pylint: disable=protected-access
    api.runs.close_run.side_effect = OSError("boom")

    assert reporter._TestRailResultsReporter__close_run() is False  # pylint: disable=protected-access,no-member
