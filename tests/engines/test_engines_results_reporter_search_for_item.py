# -*- coding: utf-8 -*-
"""Tests for results_reporter module, the TestRailResultsReporter class, internal __search_for_item method"""

from testrail_api_reporter.engines.results_reporter import (  # pylint: disable=import-error,no-name-in-module
    TestRailResultsReporter,
)


def test_search_for_item_found():
    """When a matching item exists, it should be returned directly"""
    items = [{"id": 1}, {"id": 2}, {"id": 3}]

    result = (
        TestRailResultsReporter._TestRailResultsReporter__search_for_item(  # pylint: disable=protected-access,no-member
            searched_value=2, list_to_seek=items, field="id"
        )
    )

    assert result == {"id": 2}


def test_search_for_item_not_found():
    """When no matching item exists, an empty list should be returned"""
    items = [{"id": 1}, {"id": 2}]

    result = (
        TestRailResultsReporter._TestRailResultsReporter__search_for_item(  # pylint: disable=protected-access,no-member
            searched_value=999, list_to_seek=items, field="id"
        )
    )

    assert result == []
