""" TestRails backup module """

import os
from datetime import datetime

from ..utils.logger_config import setup_logger, DEFAULT_LOGGING_LEVEL
from ..utils.reporter_utils import delete_file, zip_file


class TCBackup:
    """TestRails backup class"""

    def __init__(
        self,
        test_rails_url,
        test_rails_username,
        test_rails_password,
        test_rails_suite,
        cleanup_needed=True,
        backup_filename="backup.xml",
        cookie_name="cookie.txt",
        logger=None,
        log_level=DEFAULT_LOGGING_LEVEL,
    ):
        """
        General init

        :param test_rails_url: TestRails server url, string, i.e. https://wwakabobik.testrails.io
        :param test_rails_username: TestRails username, string, i.e. my@email.com, should have rights to make exports
        :param test_rails_password: TestRails password, string
        :param test_rails_suite: TestRails suite which needs to be downloaded, i.e. 42
        :param backup_filename: output backup file name, string, optional, by default it is backup.xml
        :param cookie_name: filename where TestRail cookie will be stored, string, by default is cookie.txt
        :param cleanup_needed: delete or not cookie file after backup, bool, True or False, by default is True
        :param logger: logger object, optional
        :param log_level: logging level, optional, by default is 'logging.DEBUG'
        """
        if not logger:
            self.___logger = setup_logger(name="TCBackup", log_file="TCBackup.log", level=log_level)
        else:
            self.___logger = logger
        self.___logger.debug("Initializing TestRails Backup")
        # TestRails
        self.__url = test_rails_url
        self.__username = test_rails_username
        self.__password = test_rails_password
        self.__suite = test_rails_suite
        # Service
        self.__cleanup_needed = cleanup_needed
        self.__backup_filename = backup_filename
        self.__cookie_name = cookie_name

    # TestRails part
    def __get_tr_cookie(self):
        """
        Login into TestRails and save session cookie

        :return: None
        """
        self.___logger.debug("Get cookie %s from %s for %s", self.__cookie_name, self.__url, self.__username)
        os.popen(
            f"curl -c {self.__cookie_name} "
            f'-H "Content-Type: application/x-www-form-urlencoded" '
            f'-d "name={self.__username}&password={self.__password}" -X POST '
            f'"{self.__url}/index.php?/auth/login"'
        ).read()

    def __download_tr_xml(self, filename=None, suite=None):
        """
        Download from TestRails XML file with testcases of testsuite

        :param filename: output backup file name, string, optional, by default it is backup.xml
        :param suite: TestRails suite which needs to be downloaded, i.e., 42
        :return: backup filename
        """
        if not filename:
            filename = self.__backup_filename
        if not suite:
            suite = self.__suite
        self.___logger.debug("Download XML %s from from %s", filename, self.__url)
        os.popen(
            f"curl -b {self.__cookie_name} " f'"{self.__url}/index.php?/suites/export/{suite}" ' f"--output {filename}"
        ).read()
        return filename

    def get_backup(self, filename=None, suite=None):
        """
        Download from TestRails backup file and deletes cookie if needed

        :param filename: output backup file name, string, optional, by default it is backup.xml
        :param suite: TestRails suite which needs to be downloaded, i.e., 42
        :return: backup filename
        """
        if not filename:
            filename = self.__backup_filename
        if not suite:
            suite = self.__suite
        self.__get_tr_cookie()
        backup_file = self.__download_tr_xml(filename=filename, suite=suite)
        if self.__cleanup_needed:
            delete_file(
                filename=self.__cookie_name,
                debug=self.___logger.debug == DEFAULT_LOGGING_LEVEL,
                logger=self.___logger,
            )
        return backup_file

    def get_archive_backup(self, filename=None, suite=None, suffix=f'_{datetime.today().strftime("%A")}'):
        """
        Download from TestRails backup file, add it to ZIP and deletes original backup file if needed

        :param filename: output backup file name, string, optional, by default it is backup.xml
        :param suite: TestRails suite which needs to be downloaded, i.e., 42
        :param suffix: suffix for backup archive, by default it "_DayOfWeek"
        :return: backup filename
        """
        if not filename:
            filename = self.__backup_filename
        if not suite:
            suite = self.__suite
        self.get_backup(filename=filename, suite=suite)
        backup_file = zip_file(
            filename=filename,
            suffix=suffix,
            debug=self.___logger.debug == DEFAULT_LOGGING_LEVEL,
            logger=self.___logger,
        )
        if self.__cleanup_needed:
            delete_file(filename=filename, debug=self.___logger.debug == DEFAULT_LOGGING_LEVEL)
        return backup_file
