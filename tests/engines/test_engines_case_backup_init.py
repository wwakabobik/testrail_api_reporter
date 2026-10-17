# -*- coding: utf-8 -*-
"""Tests for case_backup module, the TCBackup class, init method"""

from logging import getLogger, INFO, WARNING, ERROR, FATAL
from os import path, remove
from random import choice

from faker import Faker

from testrail_api_reporter.engines.case_backup import (  # pylint: disable=import-error,no-name-in-module
    TCBackup,
)
from testrail_api_reporter.utils.logger_config import (  # pylint: disable=import-error,no-name-in-module
    setup_logger,
    DEFAULT_LOGGING_LEVEL,
)

fake = Faker()


def test_case_backup_init_default_params():
    """Init TCBackup with default parameters"""
    url = fake.url()
    username = fake.email()
    password = fake.password()
    suite = fake.random_int()

    backup = TCBackup(
        test_rails_url=url, test_rails_username=username, test_rails_password=password, test_rails_suite=suite
    )

    logger = getLogger("TCBackup")
    assert logger.level == DEFAULT_LOGGING_LEVEL
    assert path.exists("TCBackup.log")

    attributes = vars(backup)
    assert attributes["_TCBackup__url"] == url
    assert attributes["_TCBackup__username"] == username
    assert attributes["_TCBackup__password"] == password
    assert attributes["_TCBackup__suite"] == suite
    assert attributes["_TCBackup__cleanup_needed"] is True
    assert attributes["_TCBackup__backup_filename"] == "backup.xml"
    assert attributes["_TCBackup__cookie_name"] == "cookie.txt"


def test_case_backup_init_custom_params():
    """Init TCBackup with custom parameters"""
    logger_file = fake.file_name(extension="log")
    logger_name = fake.name()
    logger_level = choice((INFO, WARNING, ERROR, FATAL))
    try:
        logger = setup_logger(logger_name, logger_file, level=logger_level)
        url = fake.url()
        username = fake.email()
        password = fake.password()
        suite = fake.random_int()
        backup_filename = fake.file_name(extension="xml")
        cookie_name = fake.file_name(extension="txt")

        backup = TCBackup(
            test_rails_url=url,
            test_rails_username=username,
            test_rails_password=password,
            test_rails_suite=suite,
            cleanup_needed=False,
            backup_filename=backup_filename,
            cookie_name=cookie_name,
            logger=logger,
            log_level=INFO,
        )

        logger = getLogger(logger_name)
        assert logger.level == logger_level
        assert path.exists(logger_file)

        attributes = vars(backup)
        assert attributes["_TCBackup__backup_filename"] == backup_filename
        assert attributes["_TCBackup__cookie_name"] == cookie_name
        assert attributes["_TCBackup__cleanup_needed"] is False
    finally:
        if path.exists(logger_file):
            remove(logger_file)
