# -*- coding: utf-8 -*-
"""Tests for email_sender module, the EmailSender class, send_message method (gmail method)"""

from os import getcwd
from unittest.mock import Mock, patch

import pytest
from faker import Faker

from testrail_api_reporter.publishers.email_sender import (  # pylint: disable=import-error,no-name-in-module
    EmailSender,
)

fake = Faker()

IMAGE_FILE = f"{getcwd()}/tests/assets/test_image.png"


@pytest.fixture
def gmail_sender(create_test_file):
    """Fixture to return EmailSender configured with a (fake, but existing) gmail token"""
    return EmailSender(email=fake.email(), gmail_token=create_test_file)


@pytest.fixture
def mocked_credentials():
    """Fixture to return valid (not None, not invalid) mocked gmail credentials"""
    credentials = Mock()
    credentials.invalid = False
    return credentials


@patch("testrail_api_reporter.publishers.email_sender.discovery.build")
@patch("testrail_api_reporter.publishers.email_sender.httplib2.Http")
@patch("testrail_api_reporter.publishers.email_sender.file.Storage")
def test_send_message_gmail_success(
    mock_storage, _mock_http, mock_build, gmail_sender, mocked_credentials  # pylint: disable=redefined-outer-name
):
    """Send message via gmail with valid, already stored credentials should succeed end-to-end"""
    mock_storage.return_value.get.return_value = mocked_credentials
    mocked_credentials.authorize.return_value = Mock()
    service = Mock()
    service.users.return_value.messages.return_value.send.return_value.execute.return_value = {"id": fake.uuid4()}
    mock_build.return_value = service

    gmail_sender.send_message(files=[IMAGE_FILE], recipients=[fake.email()])

    service.users.return_value.messages.return_value.send.assert_called_once()


@patch("testrail_api_reporter.publishers.email_sender.file.Storage")
def test_gmail_get_credentials_storage_failure(mock_storage, gmail_sender):  # pylint: disable=redefined-outer-name
    """A failure opening the credential storage should be wrapped in ValueError"""
    mock_storage.side_effect = OSError("boom")
    with pytest.raises(ValueError, match="Couldn't open storage"):
        gmail_sender._EmailSender__gmail_get_credentials()  # pylint: disable=protected-access,no-member


@patch("testrail_api_reporter.publishers.email_sender.file.Storage")
def test_gmail_get_credentials_get_failure(mock_storage, gmail_sender):  # pylint: disable=redefined-outer-name
    """A failure reading stored credentials should be wrapped in ValueError"""
    mock_storage.return_value.get.side_effect = OSError("boom")
    with pytest.raises(ValueError, match="Obtaining of credentials unexpectedly failed"):
        gmail_sender._EmailSender__gmail_get_credentials()  # pylint: disable=protected-access,no-member


@patch("testrail_api_reporter.publishers.email_sender.client.flow_from_clientsecrets")
@patch("testrail_api_reporter.publishers.email_sender.file.Storage")
def test_gmail_get_credentials_no_stored_credentials_flow_failure(
    mock_storage, mock_flow_from_clientsecrets, gmail_sender  # pylint: disable=redefined-outer-name
):
    """When no credentials are stored, a failure obtaining new client secrets should be wrapped in ValueError"""
    mock_storage.return_value.get.return_value = None
    mock_flow_from_clientsecrets.side_effect = OSError("boom")
    with pytest.raises(ValueError, match="Couldn't obtain new client secrets from Google OAuth"):
        gmail_sender._EmailSender__gmail_get_credentials()  # pylint: disable=protected-access,no-member


@patch("testrail_api_reporter.publishers.email_sender.tools.run_flow")
@patch("testrail_api_reporter.publishers.email_sender.client.flow_from_clientsecrets")
@patch("testrail_api_reporter.publishers.email_sender.file.Storage")
def test_gmail_get_credentials_invalid_credentials_run_flow_failure(
    mock_storage, mock_flow_from_clientsecrets, mock_run_flow, gmail_sender  # pylint: disable=redefined-outer-name
):
    """Invalid stored credentials should trigger a new OAuth flow; a failure there is wrapped in ValueError"""
    invalid_credentials = Mock()
    invalid_credentials.invalid = True
    mock_storage.return_value.get.return_value = invalid_credentials
    mock_flow_from_clientsecrets.return_value = Mock()
    mock_run_flow.side_effect = OSError("boom")
    with pytest.raises(ValueError, match="Couldn't obtain new credential from Google OAuth"):
        gmail_sender._EmailSender__gmail_get_credentials()  # pylint: disable=protected-access,no-member


@patch("testrail_api_reporter.publishers.email_sender.tools.run_flow")
@patch("testrail_api_reporter.publishers.email_sender.client.flow_from_clientsecrets")
@patch("testrail_api_reporter.publishers.email_sender.file.Storage")
def test_gmail_get_credentials_new_flow_success(
    mock_storage, mock_flow_from_clientsecrets, mock_run_flow, gmail_sender, mocked_credentials
):  # pylint: disable=redefined-outer-name
    """When no credentials are stored, a successful OAuth flow should return the new credentials"""
    mock_storage.return_value.get.return_value = None
    flow = Mock()
    mock_flow_from_clientsecrets.return_value = flow
    mock_run_flow.return_value = mocked_credentials

    result = gmail_sender._EmailSender__gmail_get_credentials()  # pylint: disable=protected-access,no-member

    assert result is mocked_credentials
    mock_run_flow.assert_called_once_with(flow, mock_storage.return_value)


@patch("testrail_api_reporter.publishers.email_sender.file.Storage")
def test_gmail_get_credentials_already_valid(
    mock_storage, gmail_sender, mocked_credentials  # pylint: disable=redefined-outer-name
):
    """Valid, already stored credentials should be returned as-is, without starting a new OAuth flow"""
    mock_storage.return_value.get.return_value = mocked_credentials

    result = gmail_sender._EmailSender__gmail_get_credentials()  # pylint: disable=protected-access,no-member

    assert result is mocked_credentials


@patch("testrail_api_reporter.publishers.email_sender.file.Storage")
@patch("testrail_api_reporter.publishers.email_sender.os.makedirs")
def test_gmail_get_credential_path_makedirs_failure(
    mock_makedirs, _mock_storage, gmail_sender
):  # pylint: disable=redefined-outer-name
    """A failure creating the credential directory should be logged, not raised"""
    mock_makedirs.side_effect = OSError("boom")

    result = gmail_sender._EmailSender__gmail_get_credential_path()  # pylint: disable=protected-access,no-member

    assert result.endswith("gmail-python-email-send.json")


@patch("testrail_api_reporter.publishers.email_sender.httplib2.Http")
def test_gmail_send_message_authorize_failure(
    _mock_http, gmail_sender, mocked_credentials  # pylint: disable=redefined-outer-name
):
    """A failure authorizing via Google OAuth should be wrapped in ValueError"""
    mocked_credentials.authorize.side_effect = OSError("boom")
    with patch(
        "testrail_api_reporter.publishers.email_sender.EmailSender._EmailSender__gmail_get_credentials",
        return_value=mocked_credentials,
    ):
        with pytest.raises(ValueError, match="Can't authorize via Google OAuth"):
            gmail_sender._EmailSender__gmail_send_message(message=Mock())  # pylint: disable=protected-access,no-member


@patch("testrail_api_reporter.publishers.email_sender.discovery.build")
@patch("testrail_api_reporter.publishers.email_sender.httplib2.Http")
def test_gmail_send_message_build_failure(
    _mock_http, mock_build, gmail_sender, mocked_credentials  # pylint: disable=redefined-outer-name
):
    """A failure building the gmail service should be wrapped in ValueError"""
    mocked_credentials.authorize.return_value = Mock()
    mock_build.side_effect = OSError("boom")
    with patch(
        "testrail_api_reporter.publishers.email_sender.EmailSender._EmailSender__gmail_get_credentials",
        return_value=mocked_credentials,
    ):
        with pytest.raises(ValueError, match="Can't build service for Google OAuth"):
            gmail_sender._EmailSender__gmail_send_message(message=Mock())  # pylint: disable=protected-access,no-member


@patch("testrail_api_reporter.publishers.email_sender.discovery.build")
@patch("testrail_api_reporter.publishers.email_sender.httplib2.Http")
@patch("testrail_api_reporter.publishers.email_sender.base64.urlsafe_b64encode")
def test_gmail_send_message_base64_failure(
    mock_b64encode, _mock_http, mock_build, gmail_sender, mocked_credentials  # pylint: disable=redefined-outer-name
):
    """A failure encoding the payload to base64 should be wrapped in ValueError"""
    mocked_credentials.authorize.return_value = Mock()
    mock_build.return_value = Mock()
    mock_b64encode.side_effect = OSError("boom")
    message = Mock()
    message.as_bytes.return_value = b"payload"
    with patch(
        "testrail_api_reporter.publishers.email_sender.EmailSender._EmailSender__gmail_get_credentials",
        return_value=mocked_credentials,
    ):
        with pytest.raises(ValueError, match="Can't convert payload to base64"):
            gmail_sender._EmailSender__gmail_send_message(message=message)  # pylint: disable=protected-access,no-member


def test_gmail_send_message_internal_failure(gmail_sender):  # pylint: disable=redefined-outer-name
    """A failure sending the message via the gmail API should be wrapped in ValueError"""
    service = Mock()
    service.users.return_value.messages.return_value.send.return_value.execute.side_effect = OSError("boom")
    with pytest.raises(ValueError, match="Can't send mail via GMail!"):
        gmail_sender._EmailSender__gmail_send_message_internal(  # pylint: disable=protected-access,no-member
            service=service, user_id=fake.email(), message={"raw": fake.password()}
        )
