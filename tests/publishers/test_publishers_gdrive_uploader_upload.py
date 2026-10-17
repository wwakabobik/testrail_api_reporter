# -*- coding: utf-8 -*-
"""Tests for gdrive_uploader module, the GoogleDriveUploader class, upload method"""

import json
from unittest.mock import patch, Mock

from faker import Faker

from testrail_api_reporter.publishers.gdrive_uploader import (  # pylint: disable=import-error,no-name-in-module
    GoogleDriveUploader,
)

fake = Faker()


def _uploader(**kwargs):
    """Build a GoogleDriveUploader with a refresh token, so init never triggers the first-run flow"""
    return GoogleDriveUploader(
        google_id=fake.uuid4(), google_secret=fake.password(), google_api_refresh_token=fake.password(), **kwargs
    )


@patch("testrail_api_reporter.publishers.gdrive_uploader.delete_file")
@patch("testrail_api_reporter.publishers.gdrive_uploader.os.popen")
def test_upload_default_params_cleanup(mock_popen, mock_delete_file):
    """Upload with default params and cleanup needed should refresh token, upload and delete the file"""
    refresh_response = json.dumps({"access_token": fake.password()})
    upload_response = json.dumps({"id": fake.uuid4()})
    mock_popen.side_effect = [
        Mock(read=Mock(return_value=refresh_response)),
        Mock(read=Mock(return_value=upload_response)),
    ]
    uploader = _uploader()

    uploader.upload()

    assert mock_popen.call_count == 2
    mock_delete_file.assert_called_once()


@patch("testrail_api_reporter.publishers.gdrive_uploader.delete_file")
@patch("testrail_api_reporter.publishers.gdrive_uploader.os.popen")
def test_upload_no_cleanup(mock_popen, mock_delete_file):
    """Upload with cleanup disabled should not delete the backup file"""
    refresh_response = json.dumps({"access_token": fake.password()})
    upload_response = json.dumps({"id": fake.uuid4()})
    mock_popen.side_effect = [
        Mock(read=Mock(return_value=refresh_response)),
        Mock(read=Mock(return_value=upload_response)),
    ]
    uploader = _uploader(cleanup_needed=False)

    uploader.upload()

    mock_delete_file.assert_not_called()


@patch("testrail_api_reporter.publishers.gdrive_uploader.delete_file")
@patch("testrail_api_reporter.publishers.gdrive_uploader.os.popen")
def test_upload_custom_filename_and_mime_type(mock_popen, _mock_delete_file):
    """Upload with a custom filename and mime type should pass through to the upload call"""
    refresh_response = json.dumps({"access_token": fake.password()})
    upload_response = json.dumps({"id": fake.uuid4()})
    mock_popen.side_effect = [
        Mock(read=Mock(return_value=refresh_response)),
        Mock(read=Mock(return_value=upload_response)),
    ]
    uploader = _uploader()

    uploader.upload(filename=fake.file_name(extension="zip"), mime_type=fake.mime_type())

    assert mock_popen.call_count == 2


@patch("testrail_api_reporter.publishers.gdrive_uploader.delete_file")
@patch("testrail_api_reporter.publishers.gdrive_uploader.os.popen")
def test_upload_token_already_present(mock_popen, _mock_delete_file):
    """A second upload should reuse the already obtained token instead of refreshing it again"""
    refresh_response = json.dumps({"access_token": fake.password()})
    upload_response = json.dumps({"id": fake.uuid4()})
    mock_popen.side_effect = [
        Mock(read=Mock(return_value=refresh_response)),
        Mock(read=Mock(return_value=upload_response)),
        Mock(read=Mock(return_value=upload_response)),
    ]
    uploader = _uploader()

    uploader.upload()
    uploader.upload()

    # 1 refresh call + 2 upload calls = 3, the second upload must not refresh the token again
    assert mock_popen.call_count == 3


@patch("testrail_api_reporter.publishers.gdrive_uploader.os.popen")
def test_proceed_upload_default_params(mock_popen):
    """Calling the internal __proceed_upload without filename/mime_type should fall back to instance defaults"""
    refresh_response = json.dumps({"access_token": fake.password()})
    upload_response = json.dumps({"id": fake.uuid4()})
    mock_popen.side_effect = [
        Mock(read=Mock(return_value=refresh_response)),
        Mock(read=Mock(return_value=upload_response)),
    ]
    uploader = _uploader()

    uploader._GoogleDriveUploader__proceed_upload()  # pylint: disable=protected-access,no-member

    assert mock_popen.call_count == 2


@patch("testrail_api_reporter.publishers.gdrive_uploader.os.popen")
def test_upload_to_gdrive_default_params(mock_popen):
    """Calling the internal __upload_to_gdrive without filename/mime_type should fall back to instance defaults"""
    upload_response = json.dumps({"id": fake.uuid4()})
    mock_popen.return_value = Mock(read=Mock(return_value=upload_response))
    uploader = _uploader()

    uploader._GoogleDriveUploader__upload_to_gdrive()  # pylint: disable=protected-access,no-member

    mock_popen.assert_called_once()


@patch("testrail_api_reporter.publishers.gdrive_uploader.delete_file")
@patch("testrail_api_reporter.publishers.gdrive_uploader.os.popen")
def test_upload_to_gdrive_failure_response(mock_popen, mock_delete_file):
    """Upload where Google Drive returns no id should be logged as an error, not raised"""
    refresh_response = json.dumps({"access_token": fake.password()})
    upload_response = json.dumps({"id": ""})
    mock_popen.side_effect = [
        Mock(read=Mock(return_value=refresh_response)),
        Mock(read=Mock(return_value=upload_response)),
    ]
    uploader = _uploader()

    uploader.upload()

    mock_delete_file.assert_called_once()
