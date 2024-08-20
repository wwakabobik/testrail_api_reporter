"""Tests for the reporter_utils module, function 'zip_file'"""

import os
import logging
from unittest.mock import MagicMock
from testrail_api_reporter.utils.reporter_utils import zip_file  # pylint: disable=import-error,no-name-in-module

def test_zip_file_default(create_test_file):
    """Test zip file with default parameters"""
    zipped_file = zip_file(create_test_file, debug=False)
    assert os.path.exists(zipped_file) is True
    os.remove(zipped_file)
    os.remove(create_test_file)

def test_zip_file_suffix(create_test_file):
    """Test zip file with custom suffix"""
    zipped_file = zip_file(create_test_file, suffix="_suffix", debug=False)
    assert os.path.exists(zipped_file) is True
    os.remove(zipped_file)
    os.remove(create_test_file)

def test_zip_file_logger(create_test_file):
    """Test zip file with logger"""
    logger = logging.getLogger(__name__)
    logger.debug = MagicMock()
    zipped_file = zip_file(create_test_file, debug=True, logger=logger)
    assert os.path.exists(zipped_file) is True
    logger.debug.assert_called_once_with(f"ZIPped {create_test_file} to {zipped_file}")
    os.remove(zipped_file)
    os.remove(create_test_file)
