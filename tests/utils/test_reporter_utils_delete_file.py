# -*- coding: utf-8 -*-
"""Tests for the reporter_utils module, function 'delete_file'"""

from os import path, remove
from unittest.mock import MagicMock

from faker import Faker

from testrail_api_reporter.utils.reporter_utils import delete_file  # pylint: disable=import-error,no-name-in-module


def test_delete_file(create_test_file):
    """
    Test delete file

        :param create_test_file: fixture, returns filename of test file to be deleted
    """

    delete_file(create_test_file, debug=False)

    assert path.exists(create_test_file) is False


def test_delete_file_with_debug(create_test_file):
    """
    Test delete file with debug output

    :param create_test_file: fixture, returns filename of test file to be deleted
    """
    mock_logger = MagicMock()
    try:
        delete_file(create_test_file, debug=True, logger=mock_logger)

        assert path.exists(create_test_file) is False
        mock_logger.debug.assert_called_once_with(f"Removed {create_test_file}")
    finally:
        if path.exists(create_test_file):
            remove(create_test_file)


def test_delete_file_non_existent(capfd):
    """
    Test delete non-existing file

    :param capfd - fixture of cap failure logger
    """
    delete_file(f"ne_delete_{Faker().file_name()}", debug=True)
    _, err = capfd.readouterr()

    assert "No such file or directory" in err
