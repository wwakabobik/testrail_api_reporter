# -*- coding: utf-8 -*-
"""Tests for email_sender module, the EmailSender class, init method"""

from logging import getLogger, INFO, WARNING, ERROR, FATAL
from os import getcwd, path, remove
from random import choice

import pytest
from faker import Faker

from testrail_api_reporter.publishers.email_sender import (  # pylint: disable=import-error,no-name-in-module
    EmailSender,
)
from testrail_api_reporter.utils.logger_config import (  # pylint: disable=import-error,no-name-in-module
    setup_logger,
    DEFAULT_LOGGING_LEVEL,
)

fake = Faker()


def test_email_sender_init_regular():
    """Init EmailSender with regular SMTP credentials"""
    email = fake.email()
    password = fake.password()
    server_smtp = fake.domain_name()
    server_port = fake.port_number()

    sender = EmailSender(email=email, password=password, server_smtp=server_smtp, server_port=server_port)

    logger = getLogger("EmailSender")
    assert logger.level == DEFAULT_LOGGING_LEVEL
    assert path.exists("email_sender.log")

    attributes = vars(sender)
    assert attributes["_EmailSender__method"] == "regular"
    assert attributes["_EmailSender__email"] == email
    assert attributes["_EmailSender__password"] == password
    assert attributes["_EmailSender__server_smtp"] == server_smtp
    assert attributes["_EmailSender__server_port"] == server_port


def test_email_sender_init_custom_logger():
    """Init EmailSender with a custom logger"""
    logger_file = fake.file_name(extension="log")
    logger_name = fake.name()
    logger_level = choice((INFO, WARNING, ERROR, FATAL))
    try:
        logger = setup_logger(logger_name, logger_file, level=logger_level)
        sender = EmailSender(
            email=fake.email(),
            password=fake.password(),
            server_smtp=fake.domain_name(),
            server_port=fake.port_number(),
            logger=logger,
            log_level=INFO,
        )

        logger = getLogger(logger_name)
        assert logger.level == logger_level
        assert path.exists(logger_file)
        assert vars(sender)["_EmailSender__method"] == "regular"
    finally:
        if path.exists(logger_file):
            remove(logger_file)


def test_email_sender_init_gmail_absolute_path(create_test_file):
    """Init EmailSender with a gmail token given as an existing absolute path"""
    gmail_token = f"{getcwd()}/{create_test_file}"
    sender = EmailSender(email=fake.email(), gmail_token=gmail_token)

    attributes = vars(sender)
    assert attributes["_EmailSender__method"] == "gmail"
    assert attributes["_EmailSender__gmail_token"] == gmail_token


def test_email_sender_init_gmail_relative_path(create_test_file):
    """Init EmailSender with a gmail token given as an existing relative filename"""
    sender = EmailSender(email=fake.email(), gmail_token=create_test_file)

    attributes = vars(sender)
    assert attributes["_EmailSender__method"] == "gmail"


def test_email_sender_init_gmail_token_not_found():
    """Init EmailSender with a gmail token that does not exist anywhere should raise ValueError"""
    with pytest.raises(ValueError, match="No email credentials are provided, aborted!"):
        EmailSender(email=fake.email(), gmail_token=fake.file_name(extension="json"))


def test_email_sender_init_no_credentials():
    """Init EmailSender without any credentials should raise ValueError"""
    with pytest.raises(ValueError, match="No email credentials are provided, aborted!"):
        EmailSender()
