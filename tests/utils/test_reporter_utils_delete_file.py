"""Tests for the reporter_utils module, function 'delete_file'"""

import os
from unittest.mock import MagicMock

from testrail_api_reporter.utils.reporter_utils import delete_file  # pylint: disable=import-error,no-name-in-module


def test_delete_file():
    """Test delete file"""
    test_file = "test_file.txt"
    with open(test_file, "w") as file:
        file.write("Test")

    assert os.path.exists(test_file) is True
    delete_file(test_file, debug=False)

    assert os.path.exists(test_file) is False


def test_delete_file_with_debug():
    """Test delete file with debug output"""
    test_file = "test_file.txt"
    with open(test_file, "w") as file:
        file.write("Test")

    assert os.path.exists(test_file) is True
    mock_logger = MagicMock()
    delete_file(test_file, debug=True, logger=mock_logger)

    assert os.path.exists(test_file) is False
    mock_logger.debug.assert_called_once_with(f"Removed {test_file}")


def test_delete_file_non_existent(capfd):
    """
    Test delete non-existing file

    :param capfd - fixture of cap failure logger
    """
    delete_file("non_existent_file.txt", debug=True)
    out, err = capfd.readouterr()

    assert "No such file or directory" in err
