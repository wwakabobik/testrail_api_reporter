# -*- coding: utf-8 -*-
"""Tests for the reporter_utils module, function 'upload_image'"""

from os import getcwd, getenv
from random import choice
from unittest.mock import patch, Mock

from faker import Faker
from pytest import raises as pytest_raises

from testrail_api_reporter.utils.reporter_utils import upload_image  # pylint: disable=import-error,no-name-in-module


test_filename = choice((f"{getcwd()}/tests/assets/test_image.png", f"{getcwd()}/tests/assets/test_image.jpeg"))


def test_upload_image_mock_success():
    """Test success image upload (mock)"""
    with patch("requests.post") as mock_post:
        faker = Faker()
        url = faker.image_url()
        thumb_url = faker.image_url()
        mock_response = Mock()
        mock_response.json.return_value = {"image": {"url": url, "thumb": {"url": thumb_url}}}
        mock_post.return_value = mock_response
        result = upload_image(test_filename, "test_api_token")
        assert result == {"image": url, "thumb": thumb_url}


def test_upload_image_mock_nonexistent_file():
    """Test response for not existent file (mock)"""
    with pytest_raises(FileNotFoundError):
        faker = Faker()
        upload_image(faker.file_path(extension=choice(("png", "jpg", "jpeg"))), faker.password())


def test_upload_image_mock_invalid_token():
    """Test against invalid token (mock)"""
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Invalid API token"}
        mock_post.return_value = mock_response
        with pytest_raises(KeyError):
            upload_image(test_filename, Faker().password())


def test_upload_image_mock_api_error():
    """Test against API error (invalid response/request) (mock)"""
    with patch("requests.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Upload error"}
        mock_post.return_value = mock_response
        with pytest_raises(KeyError):
            upload_image(test_filename, Faker().password())


def test_upload_image_live_success():
    """Test success image upload"""
    result = upload_image(test_filename, getenv("FREEIMAGEHOST_API_KEY"))
    assert "image" in result
    assert "thumb" in result


def test_upload_image_live_nonexistent_file():
    """Test response for not existent file"""
    with pytest_raises(FileNotFoundError):
        upload_image(Faker().file_path(extension=choice(("png", "jpg", "jpeg"))), getenv("FREEIMAGEHOST_API_KEY"))


def test_upload_image_live_invalid_token():
    """Test against invalid token"""
    with pytest_raises(KeyError):
        upload_image(test_filename, Faker().password())
