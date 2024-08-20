"""Tests for the reporter_utils module, function 'delete_file'"""

from os import path
from unittest.mock import MagicMock

from faker import Faker

from testrail_api_reporter.utils.reporter_utils import delete_file  # pylint: disable=import-error,no-name-in-module


def test_delete_file(create_test_file):
    """Test delete file"""

    delete_file(create_test_file, debug=False)

    assert path.exists(create_test_file) is False


def test_delete_file_with_debug(create_test_file):
    """Test delete file with debug output"""
    mock_logger = MagicMock()
    delete_file(create_test_file, debug=True, logger=mock_logger)

    assert path.exists(create_test_file) is False
    mock_logger.debug.assert_called_once_with(f"Removed {create_test_file}")


def test_delete_file_non_existent(capfd):
    """
    Test delete non-existing file

    :param capfd - fixture of cap failure logger
    """
    delete_file(Faker().file_name(), debug=True)
    _, err = capfd.readouterr()

    assert "No such file or directory" in err
