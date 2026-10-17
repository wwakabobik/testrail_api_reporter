# -*- coding: utf-8 -*-
"""Live tests for TCBackup against a real TestRail instance (legacy web UI XML suite export)

Note: TCBackup logs in via the legacy web UI form, not the REST API, so it needs a real account
password rather than an API key - see the warning in TCBackup's docstring. If TESTRAIL_PASSWORD is
an API key (not the login password), these tests will fail to authenticate even though every other
live test in this package works fine with it.
"""

from os import getenv
from os.path import exists

import pytest

from testrail_api_reporter.engines.case_backup import TCBackup  # pylint: disable=import-error,no-name-in-module

requires_live_testrail = pytest.mark.skipif(
    not (
        getenv("TESTRAIL_URL")
        and getenv("TESTRAIL_EMAIL")
        and getenv("TESTRAIL_PASSWORD")
        and getenv("TESTRAIL_PROJECT_ID")
    ),
    reason="Live TestRail tests require TESTRAIL_URL, TESTRAIL_EMAIL, TESTRAIL_PASSWORD and TESTRAIL_PROJECT_ID",
)


@requires_live_testrail
def test_get_backup_downloads_xml_file(tr_url, tr_email, tr_password, tr_suite_id, tmp_path):
    """get_backup should log in, download the suite export and return the local filename"""
    if not tr_suite_id:
        pytest.skip("TESTRAIL_SUITE_ID is required for the legacy suite export used by TCBackup")
    filename = str(tmp_path / "live_backup.xml")

    backup = TCBackup(
        test_rails_url=tr_url,
        test_rails_username=tr_email,
        test_rails_password=tr_password,
        test_rails_suite=tr_suite_id,
        backup_filename=filename,
        cookie_name=str(tmp_path / "live_cookie.txt"),
    )

    result = backup.get_backup()

    assert result == filename
    assert exists(filename)
    with open(filename, "r", encoding="utf-8") as backup_file:
        content = backup_file.read()
    assert "<suite" in content
