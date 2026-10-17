# -*- coding: utf-8 -*-
"""Tests for the reporter_utils module, function 'upload_image'"""

from os import getcwd, getenv, remove
from os.path import exists
from random import choice, randint
from unittest.mock import patch, Mock

from faker import Faker
from PIL import Image
from pytest import raises as pytest_raises
from requests import post as requests_post

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
    """
    Test success image upload

    Generates a fresh, randomly-colored image for each run instead of reusing the static fixture, and
    surfaces the raw API response on failure: freeimage.host has been rejecting uploads lately for a
    reason that isn't yet confirmed (duplicate content was ruled out once this fixture became unique
    per run), so a bare KeyError on CI gives no way to tell an auth/key problem from anything else.
    """
    unique_filename = f"{getcwd()}/tests/assets/live_upload_{randint(1, 2**31)}.png"
    api_token = getenv("FREEIMAGEHOST_API_KEY")
    try:
        Image.new("RGB", (8, 8), color=(randint(0, 255), randint(0, 255), randint(0, 255))).save(unique_filename)
        try:
            result = upload_image(unique_filename, api_token)
        except KeyError as error:
            payload = {"action": "upload", "key": api_token, "format": "json"}
            with open(unique_filename, "rb") as source_file:
                diagnostic_response = requests_post(
                    url="https://freeimage.host/api/1/upload",
                    data=payload,
                    timeout=5,
                    verify=True,
                    files={"source": source_file},
                )
            raise AssertionError(
                f"upload_image raised {error!r}; raw API response was "
                f"{diagnostic_response.status_code}: {diagnostic_response.text}"
            ) from error
        assert "image" in result
        assert "thumb" in result
    finally:
        if exists(unique_filename):
            remove(unique_filename)


def test_upload_image_live_nonexistent_file():
    """Test response for not existent file"""
    with pytest_raises(FileNotFoundError):
        upload_image(Faker().file_path(extension=choice(("png", "jpg", "jpeg"))), getenv("FREEIMAGEHOST_API_KEY"))


def test_upload_image_live_invalid_token():
    """Test against invalid token"""
    with pytest_raises(KeyError):
        upload_image(test_filename, Faker().password())
