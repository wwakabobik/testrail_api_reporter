# -*- coding: utf-8 -*-
"""Tests for the reporter_utils module, function 'init_get_cases_process'"""

from testrail_api_reporter.utils.reporter_utils import (  # pylint: disable=import-error,no-name-in-module
    init_get_cases_process,
)


def test_init_get_cases_process():
    """Test init_get_cases_process"""
    cases_list, first_run, criteria, response, retry = init_get_cases_process()

    assert isinstance(cases_list, list)
    assert cases_list == []
    assert first_run is True
    assert criteria is None
    assert response is None
    assert retry == 0
