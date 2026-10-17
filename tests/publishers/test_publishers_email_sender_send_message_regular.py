# -*- coding: utf-8 -*-
"""Tests for email_sender module, the EmailSender class, send_message method (regular/SMTP method)"""

from os import getcwd
from random import randint
from unittest.mock import Mock, patch

import pytest
from faker import Faker

from testrail_api_reporter.publishers.email_sender import (  # pylint: disable=import-error,no-name-in-module
    EmailSender,
)

fake = Faker()

IMAGE_FILE = f"{getcwd()}/tests/assets/test_image.png"


@pytest.fixture
def email_sender():
    """Fixture to return EmailSender configured with regular SMTP credentials"""
    return EmailSender(
        email=fake.email(), password=fake.password(), server_smtp=fake.domain_name(), server_port=fake.port_number()
    )


def test_send_message_no_files(email_sender):  # pylint: disable=redefined-outer-name
    """Send message without a file list and without a custom message should raise ValueError"""
    with pytest.raises(ValueError, match="No file list for report provided, aborted!"):
        email_sender.send_message(files=None, recipients=[fake.email()])


def test_send_message_invalid_recipients(email_sender):  # pylint: disable=redefined-outer-name
    """Send message with invalid recipients (not a str nor a list) should raise ValueError"""
    with pytest.raises(ValueError, match="Wrong list of recipients is provided, aborted!"):
        email_sender.send_message(files=[IMAGE_FILE], recipients=123)


@patch("testrail_api_reporter.publishers.email_sender.smtplib.SMTP")
def test_send_message_success_recipient_str(mock_smtp, email_sender):  # pylint: disable=redefined-outer-name
    """Send message with a single recipient as a string should wrap it into a list and succeed"""
    connection = Mock()
    mock_smtp.return_value = connection

    email_sender.send_message(files=[IMAGE_FILE], recipients=fake.email())

    connection.sendmail.assert_called_once()
    connection.quit.assert_called_once()


@patch("testrail_api_reporter.publishers.email_sender.smtplib.SMTP")
def test_send_message_success_recipients_list(mock_smtp, email_sender):  # pylint: disable=redefined-outer-name
    """Send message with multiple recipients and captions should succeed"""
    connection = Mock()
    mock_smtp.return_value = connection
    files = [IMAGE_FILE for _ in range(randint(1, 3))]
    captions = [fake.sentence() for _ in files]

    email_sender.send_message(
        files=files,
        captions=captions,
        recipients=[fake.email() for _ in range(randint(1, 3))],
        title=fake.sentence(),
        timestamp=fake.date(),
    )

    connection.sendmail.assert_called_once()


@patch("testrail_api_reporter.publishers.email_sender.smtplib.SMTP")
def test_send_message_custom_message(mock_smtp, email_sender):  # pylint: disable=redefined-outer-name
    """Send message with a custom_message should bypass file/recipients validation and payload preparation"""
    connection = Mock()
    mock_smtp.return_value = connection

    email_sender.send_message(files="not-a-list", recipients=123, custom_message=Mock())

    connection.sendmail.assert_called_once()


@patch("testrail_api_reporter.publishers.email_sender.smtplib.SMTP")
def test_send_message_method_override(mock_smtp, email_sender):  # pylint: disable=redefined-outer-name
    """Send message with an explicit method that is neither 'regular' nor 'gmail' should send nothing"""
    email_sender.send_message(files=[IMAGE_FILE], recipients=[fake.email()], method=fake.word())

    mock_smtp.assert_not_called()


@patch("testrail_api_reporter.publishers.email_sender.smtplib.SMTP")
def test_send_message_connect_failure(mock_smtp, email_sender):  # pylint: disable=redefined-outer-name
    """A failure while connecting to the mail server should be wrapped in ValueError"""
    mock_smtp.side_effect = OSError("boom")
    with pytest.raises(ValueError, match="Can't login to mail!"):
        email_sender.send_message(files=[IMAGE_FILE], recipients=[fake.email()])


@patch("testrail_api_reporter.publishers.email_sender.smtplib.SMTP")
def test_send_message_send_failure(mock_smtp, email_sender):  # pylint: disable=redefined-outer-name
    """A failure while sending mail should be wrapped in ValueError"""
    connection = Mock()
    connection.sendmail.side_effect = OSError("boom")
    mock_smtp.return_value = connection
    with pytest.raises(ValueError, match="Can't send mail!"):
        email_sender.send_message(files=[IMAGE_FILE], recipients=[fake.email()])


@patch("testrail_api_reporter.publishers.email_sender.smtplib.SMTP")
def test_send_message_disconnect_failure(mock_smtp, email_sender):  # pylint: disable=redefined-outer-name
    """A failure while disconnecting from the mail server should be wrapped in ValueError"""
    connection = Mock()
    connection.quit.side_effect = OSError("boom")
    mock_smtp.return_value = connection
    with pytest.raises(ValueError, match="Can't close connection!"):
        email_sender.send_message(files=[IMAGE_FILE], recipients=[fake.email()])
