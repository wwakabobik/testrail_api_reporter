# -*- coding: utf-8 -*-
"""Tests for case_backup module, the TCBackup class, get_archive_backup method"""

from unittest.mock import patch, Mock

from faker import Faker

from testrail_api_reporter.engines.case_backup import (  # pylint: disable=import-error,no-name-in-module
    TCBackup,
)

fake = Faker()


@patch("testrail_api_reporter.engines.case_backup.os.popen")
def test_get_archive_backup_default_params(mock_popen):
    """Call get_archive_backup with default params, cleanup needed, should zip and delete the backup file"""
    mock_popen.return_value = Mock(read=Mock(return_value=""))
    backup = TCBackup(
        test_rails_url=fake.url(),
        test_rails_username=fake.email(),
        test_rails_password=fake.password(),
        test_rails_suite=fake.random_int(),
    )
    zipped_file = fake.file_name(extension="zip")
    with patch("testrail_api_reporter.engines.case_backup.zip_file", return_value=zipped_file) as mock_zip_file, patch(
        "testrail_api_reporter.engines.case_backup.delete_file"
    ) as mock_delete_file:
        result = backup.get_archive_backup()
        assert result == zipped_file
        mock_zip_file.assert_called_once()
        # delete_file is called twice: once for the cookie (inside get_backup) and once for the backup file
        assert mock_delete_file.call_count == 2


@patch("testrail_api_reporter.engines.case_backup.os.popen")
def test_get_archive_backup_no_cleanup(mock_popen):
    """Call get_archive_backup with cleanup disabled should not delete the backup file"""
    mock_popen.return_value = Mock(read=Mock(return_value=""))
    backup = TCBackup(
        test_rails_url=fake.url(),
        test_rails_username=fake.email(),
        test_rails_password=fake.password(),
        test_rails_suite=fake.random_int(),
        cleanup_needed=False,
    )
    zipped_file = fake.file_name(extension="zip")
    with patch("testrail_api_reporter.engines.case_backup.zip_file", return_value=zipped_file) as mock_zip_file, patch(
        "testrail_api_reporter.engines.case_backup.delete_file"
    ) as mock_delete_file:
        result = backup.get_archive_backup()
        assert result == zipped_file
        mock_zip_file.assert_called_once()
        mock_delete_file.assert_not_called()


@patch("testrail_api_reporter.engines.case_backup.os.popen")
def test_get_archive_backup_custom_params(mock_popen):
    """Call get_archive_backup with custom filename, suite and suffix should pass them through"""
    mock_popen.return_value = Mock(read=Mock(return_value=""))
    backup = TCBackup(
        test_rails_url=fake.url(),
        test_rails_username=fake.email(),
        test_rails_password=fake.password(),
        test_rails_suite=fake.random_int(),
        cleanup_needed=False,
    )
    filename = fake.file_name(extension="xml")
    suite = fake.random_int()
    suffix = f"_{fake.word()}"
    zipped_file = fake.file_name(extension="zip")
    with patch("testrail_api_reporter.engines.case_backup.zip_file", return_value=zipped_file) as mock_zip_file:
        result = backup.get_archive_backup(filename=filename, suite=suite, suffix=suffix)
        assert result == zipped_file
        mock_zip_file.assert_called_once_with(
            filename=filename,
            suffix=suffix,
            debug=False,
            logger=backup._TCBackup___logger,  # pylint: disable=protected-access,no-member
        )
