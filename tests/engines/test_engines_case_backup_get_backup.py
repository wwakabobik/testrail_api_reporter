# -*- coding: utf-8 -*-
"""Tests for case_backup module, the TCBackup class, get_backup method"""

from unittest.mock import patch, Mock

from faker import Faker

from testrail_api_reporter.engines.case_backup import (  # pylint: disable=import-error,no-name-in-module
    TCBackup,
)

fake = Faker()


@patch("testrail_api_reporter.engines.case_backup.os.popen")
def test_get_backup_default_params(mock_popen):
    """Call get_backup with default params, cleanup needed, should download XML and delete cookie"""
    mock_popen.return_value = Mock(read=Mock(return_value=""))
    backup = TCBackup(
        test_rails_url=fake.url(),
        test_rails_username=fake.email(),
        test_rails_password=fake.password(),
        test_rails_suite=fake.random_int(),
    )
    with patch("testrail_api_reporter.engines.case_backup.delete_file") as mock_delete_file:
        result = backup.get_backup()
        assert result == "backup.xml"
        mock_delete_file.assert_called_once()


@patch("testrail_api_reporter.engines.case_backup.os.popen")
def test_get_backup_no_cleanup(mock_popen):
    """Call get_backup with cleanup disabled should not delete the cookie file"""
    mock_popen.return_value = Mock(read=Mock(return_value=""))
    backup = TCBackup(
        test_rails_url=fake.url(),
        test_rails_username=fake.email(),
        test_rails_password=fake.password(),
        test_rails_suite=fake.random_int(),
        cleanup_needed=False,
    )
    with patch("testrail_api_reporter.engines.case_backup.delete_file") as mock_delete_file:
        result = backup.get_backup()
        assert result == "backup.xml"
        mock_delete_file.assert_not_called()


@patch("testrail_api_reporter.engines.case_backup.os.popen")
def test_get_backup_custom_params(mock_popen):
    """Call get_backup with custom filename and suite should pass them through"""
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
    result = backup.get_backup(filename=filename, suite=suite)
    assert result == filename


@patch("testrail_api_reporter.engines.case_backup.os.popen")
def test_download_tr_xml_default_params(mock_popen):
    """Call the internal __download_tr_xml without filename/suite should fall back to instance defaults"""
    mock_popen.return_value = Mock(read=Mock(return_value=""))
    backup = TCBackup(
        test_rails_url=fake.url(),
        test_rails_username=fake.email(),
        test_rails_password=fake.password(),
        test_rails_suite=fake.random_int(),
    )
    result = backup._TCBackup__download_tr_xml()  # pylint: disable=protected-access,no-member
    assert result == "backup.xml"
