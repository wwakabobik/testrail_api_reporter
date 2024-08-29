# -*- coding: utf-8 -*-
"""Tests for the reporter_utils module, function 'check_captions_and_files'"""

from logging import getLogger
from random import randint
from unittest.mock import MagicMock

from faker import Faker

from testrail_api_reporter.utils.reporter_utils import (  # pylint: disable=import-error,no-name-in-module
    check_captions_and_files,
)

faker = Faker()


def test_check_captions_and_files_not_list():
    """Test check_captions_and_files when captions is not a list"""
    captions = faker.sentence()
    files = [faker.file_name() for _ in range(randint(1, 10))]

    logger = getLogger(__name__)
    logger.debug = MagicMock()

    result = check_captions_and_files(captions, files, debug=True, logger=logger)
    assert result is None
    logger.debug.assert_called_once_with("Captions are not a list, thus no legend will be displayed")


def test_check_captions_and_files_different_length():
    """Test check_captions_and_files when captions and files have different lengths"""
    captions = [faker.sentence() for _ in range(randint(1, 10))]
    files = []
    while len(captions) == len(files):
        files = [faker.file_name() for _ in range(randint(1, 10))]

    logger = getLogger(__name__)
    logger.debug = MagicMock()

    result = check_captions_and_files(captions, files, debug=True, logger=logger)
    assert result is None
    logger.debug.assert_called_once_with(
        "Caption and file lists are not the same length %s != %s thus no legend will be displayed",
        len(captions),
        len(files),
    )


def test_check_captions_and_files_same_length():
    """Test check_captions_and_files when captions and files have the same length"""
    length = randint(1, 10)
    captions = [faker.sentence() for _ in range(length)]
    files = [faker.file_name() for _ in range(length)]

    result = check_captions_and_files(captions, files, debug=False)
    assert result == captions
