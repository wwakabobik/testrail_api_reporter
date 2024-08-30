# -*- coding: utf-8 -*-
"""Tests for the reporter_utils module, function 'zip_file'"""

from os import path, remove
import logging
from unittest.mock import MagicMock
from testrail_api_reporter.utils.reporter_utils import zip_file  # pylint: disable=import-error,no-name-in-module


def test_zip_file_default(create_test_file):
    """Test zip file with default parameters"""
    zipped_file = ""
    try:
        zipped_file = zip_file(create_test_file, debug=False)
        assert path.exists(zipped_file) is True
    finally:
        if path.exists(zipped_file):
            remove(zipped_file)
        if path.exists(create_test_file):
            remove(create_test_file)


def test_zip_file_suffix(create_test_file):
    """Test zip file with custom suffix"""
    zipped_file = ""
    try:
        zipped_file = zip_file(create_test_file, suffix="_suffix", debug=False)
        assert path.exists(zipped_file) is True
    finally:
        if path.exists(zipped_file):
            remove(zipped_file)
        if path.exists(create_test_file):
            remove(create_test_file)


def test_zip_file_logger(create_test_file):
    """Test zip file with logger"""
    zipped_file = ""
    try:
        logger = logging.getLogger(__name__)
        logger.debug = MagicMock()
        zipped_file = zip_file(create_test_file, debug=True, logger=logger)
        assert path.exists(zipped_file) is True
        logger.debug.assert_called_once_with(f"ZIPped {create_test_file} to {zipped_file}")
    finally:
        if path.exists(zipped_file):
            remove(zipped_file)
        if path.exists(create_test_file):
            remove(create_test_file)
