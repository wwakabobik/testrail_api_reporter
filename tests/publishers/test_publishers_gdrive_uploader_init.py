# -*- coding: utf-8 -*-
"""Tests for gdrive_uploader module, the GoogleDriveUploader class, init method"""

import json
from logging import getLogger, INFO, WARNING, ERROR, FATAL
from os import path, remove
from random import choice
from unittest.mock import patch, Mock

from faker import Faker

from testrail_api_reporter.publishers.gdrive_uploader import (  # pylint: disable=import-error,no-name-in-module
    GoogleDriveUploader,
)
from testrail_api_reporter.utils.logger_config import (  # pylint: disable=import-error,no-name-in-module
    setup_logger,
    DEFAULT_LOGGING_LEVEL,
)

fake = Faker()


def test_gdrive_uploader_init_with_refresh_token():
    """Init GoogleDriveUploader with a refresh token provided should skip the first-run flow"""
    google_id = fake.uuid4()
    google_secret = fake.password()
    refresh_token = fake.password()

    uploader = GoogleDriveUploader(
        google_id=google_id, google_secret=google_secret, google_api_refresh_token=refresh_token
    )

    logger = getLogger("GoogleDriveUploader")
    assert logger.level == DEFAULT_LOGGING_LEVEL
    assert path.exists("GoogleDriveUploader.log")

    attributes = vars(uploader)
    assert attributes["_GoogleDriveUploader__g_id"] == google_id
    assert attributes["_GoogleDriveUploader__g_secret"] == google_secret
    assert attributes["_GoogleDriveUploader__g_token"] is None
    assert attributes["_GoogleDriveUploader__g_refresh_token"] == refresh_token
    assert attributes["_GoogleDriveUploader__cleanup_needed"] is True
    assert attributes["_GoogleDriveUploader__backup_filename"] == "backup.zip"
    assert attributes["_GoogleDriveUploader__mime_type"] == "application/zip"


def test_gdrive_uploader_init_custom_params():
    """Init GoogleDriveUploader with custom parameters"""
    logger_file = fake.file_name(extension="log")
    logger_name = fake.name()
    logger_level = choice((INFO, WARNING, ERROR, FATAL))
    try:
        logger = setup_logger(logger_name, logger_file, level=logger_level)
        backup_filename = fake.file_name(extension="zip")
        mime_type = fake.mime_type()

        uploader = GoogleDriveUploader(
            google_id=fake.uuid4(),
            google_secret=fake.password(),
            google_api_refresh_token=fake.password(),
            cleanup_needed=False,
            backup_filename=backup_filename,
            mime_type=mime_type,
            logger=logger,
            log_level=INFO,
        )

        logger = getLogger(logger_name)
        assert logger.level == logger_level
        assert path.exists(logger_file)

        attributes = vars(uploader)
        assert attributes["_GoogleDriveUploader__cleanup_needed"] is False
        assert attributes["_GoogleDriveUploader__backup_filename"] == backup_filename
        assert attributes["_GoogleDriveUploader__mime_type"] == mime_type
    finally:
        if path.exists(logger_file):
            remove(logger_file)


@patch("builtins.input", return_value="")
@patch("testrail_api_reporter.publishers.gdrive_uploader.os.popen")
def test_gdrive_uploader_init_first_run_no_refresh_token(mock_popen, _mock_input):
    """Init GoogleDriveUploader without a refresh token should perform the device code first-run flow"""
    device_response = json.dumps(
        {"device_code": fake.uuid4(), "user_code": fake.word(), "verification_url": fake.url()}
    )
    oauth_response = json.dumps({"access_token": fake.password(), "refresh_token": fake.password()})
    mock_popen.side_effect = [Mock(read=Mock(return_value=device_response)), Mock(read=Mock(return_value=oauth_response))]

    uploader = GoogleDriveUploader(google_id=fake.uuid4(), google_secret=fake.password())

    attributes = vars(uploader)
    assert attributes["_GoogleDriveUploader__g_token"] == json.loads(oauth_response)["access_token"]
    assert attributes["_GoogleDriveUploader__g_refresh_token"] == json.loads(oauth_response)["refresh_token"]
    assert mock_popen.call_count == 2


@patch("builtins.input", return_value="")
@patch("testrail_api_reporter.publishers.gdrive_uploader.os.popen")
def test_gdrive_uploader_init_first_run_empty_refresh_token(mock_popen, _mock_input):
    """Init GoogleDriveUploader with an empty-string refresh token should also perform the first-run flow"""
    device_response = json.dumps(
        {"device_code": fake.uuid4(), "user_code": fake.word(), "verification_url": fake.url()}
    )
    oauth_response = json.dumps({"access_token": fake.password(), "refresh_token": fake.password()})
    mock_popen.side_effect = [Mock(read=Mock(return_value=device_response)), Mock(read=Mock(return_value=oauth_response))]

    uploader = GoogleDriveUploader(google_id=fake.uuid4(), google_secret=fake.password(), google_api_refresh_token="")

    attributes = vars(uploader)
    assert attributes["_GoogleDriveUploader__g_refresh_token"] == json.loads(oauth_response)["refresh_token"]
