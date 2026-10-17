# -*- coding: utf-8 -*-
"""Tests for slack_sender module, the SlackSender class, send_message method"""

from random import randint
from unittest.mock import patch, Mock

import pytest
from faker import Faker

from testrail_api_reporter.publishers.slack_sender import (  # pylint: disable=import-error,no-name-in-module
    SlackSender,
)

fake = Faker()


@pytest.fixture
def slack_sender():
    """Fixture to return SlackSender object with a fake hook url"""
    return SlackSender(hook_url=fake.url())


def test_send_message_no_files(slack_sender):  # pylint: disable=redefined-outer-name
    """Send message without files should raise ValueError"""
    with pytest.raises(ValueError, match="No file list for report provided, aborted!"):
        slack_sender.send_message(files=None)


def test_send_message_success(slack_sender):  # pylint: disable=redefined-outer-name
    """Send message with valid files should succeed"""
    files = [fake.image_url() for _ in range(randint(1, 5))]
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        slack_sender.send_message(files=files)
        mock_post.assert_called_once()


def test_send_message_with_captions(slack_sender):  # pylint: disable=redefined-outer-name
    """Send message with valid files and captions should succeed"""
    files = [fake.image_url() for _ in range(randint(1, 5))]
    captions = [fake.sentence() for _ in range(len(files))]
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        slack_sender.send_message(files=files, captions=captions, title=fake.sentence())
        mock_post.assert_called_once()


def test_send_message_bad_status_code(slack_sender):  # pylint: disable=redefined-outer-name
    """Send message when Slack responds with a non-200 status code should raise ValueError"""
    files = [fake.image_url() for _ in range(randint(1, 5))]
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "not_found"
        mock_response.raise_for_status = Mock(return_value=None)
        mock_post.return_value = mock_response
        with pytest.raises(ValueError, match="Message can't be sent!"):
            slack_sender.send_message(files=files)


def test_send_message_request_exception(slack_sender):  # pylint: disable=redefined-outer-name
    """Send message when requests.post raises an exception should raise ValueError"""
    files = [fake.image_url() for _ in range(randint(1, 5))]
    with patch("requests.post", side_effect=ConnectionError("boom")):
        with pytest.raises(ValueError, match="Message can't be sent!"):
            slack_sender.send_message(files=files)
