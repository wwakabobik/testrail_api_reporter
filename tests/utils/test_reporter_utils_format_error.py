# -*- coding: utf-8 -*-
"""Tests for the reporter_utils module, function 'format_error'"""

from testrail_api_reporter.utils.reporter_utils import format_error  # pylint: disable=import-error,no-name-in-module


def test_format_error_single_string():
    """Test with single string error"""
    error = "Error occurred"
    expected_result = " : Error occurred"
    assert format_error(error) == expected_result


def test_format_error_list_with_single_error():
    """Test with single error in list"""
    error = ["Error occurred"]
    expected_result = " : Error occurred"
    assert format_error(error) == expected_result


def test_format_error_list_with_multiple_errors():
    """Test with multiple errors in list"""
    error = ["Error one", "Error two"]
    expected_result = " : Error one : Error two"
    assert format_error(error) == expected_result


def test_format_error_empty_list():
    """Test with empty list of errors"""
    error = []
    expected_result = ""
    assert format_error(error) == expected_result


def test_format_error_non_list_non_string():
    """Test with non-list and non-string error"""
    error = Exception("An exception occurred")
    expected_result = " : An exception occurred"
    assert format_error(error) == expected_result


def test_format_error_list_with_mixed_types():
    """Test with mixed types in list"""
    error = ["Error one", Exception("An exception occurred")]
    expected_result = " : Error one : An exception occurred"
    assert format_error(error) == expected_result


def test_format_error_list_with_empty_string():
    """Test with empty string in list"""
    error = ["Error one", ""]
    expected_result = " : Error one : "
    assert format_error(error) == expected_result


def test_format_error_list_with_empty_string_and_exception():
    """Test with empty string and exception in list"""
    error = ["Error one", "", Exception("An exception occurred")]
    expected_result = " : Error one :  : An exception occurred"
    assert format_error(error) == expected_result


def test_format_error_list_with_empty_string_and_exception_and_none():
    """Test with empty string, exception and None in list"""
    error = ["Error one", "", Exception("An exception occurred"), None]
    expected_result = " : Error one :  : An exception occurred : None"
    assert format_error(error) == expected_result


def test_format_error_list_with_none():
    """Test with None in list"""
    error = [None]
    expected_result = " : None"
    assert format_error(error) == expected_result


def test_format_error_none():
    """Test with None"""
    error = None
    expected_result = " : None"
    assert format_error(error) == expected_result


def test_format_error_value_error():
    """Test with ValueError"""
    error = ValueError("A value error occurred")
    expected_result = " : A value error occurred"
    assert format_error(error) == expected_result
