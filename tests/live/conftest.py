# -*- coding: utf-8 -*-
"""Conftest for live tests - these hit a real TestRail instance instead of mocking TestRailAPI.

Credentials are read from the same env var names the `testrail-api` package itself recognizes
(TESTRAIL_URL, TESTRAIL_EMAIL, TESTRAIL_PASSWORD), plus TESTRAIL_PROJECT_ID/TESTRAIL_SUITE_ID for
this library's own tests. Tests are skipped automatically when these aren't set, so they're opt-in
locally and in CI (CI needs the corresponding secrets added to the workflow to actually exercise them).

A dedicated, disposable TestRail project/suite should be used - these tests create and delete
sections, cases and runs.
"""

from os import getenv

import pytest

TESTRAIL_URL = getenv("TESTRAIL_URL")
TESTRAIL_EMAIL = getenv("TESTRAIL_EMAIL")
TESTRAIL_PASSWORD = getenv("TESTRAIL_PASSWORD")
TESTRAIL_PROJECT_ID = getenv("TESTRAIL_PROJECT_ID")
TESTRAIL_SUITE_ID = getenv("TESTRAIL_SUITE_ID")

# Each test module redefines this skip condition locally (no __init__.py in tests/, so relative
# imports from conftest aren't available); keep the env var names in sync with the ones above.
requires_live_testrail = pytest.mark.skipif(
    not (TESTRAIL_URL and TESTRAIL_EMAIL and TESTRAIL_PASSWORD and TESTRAIL_PROJECT_ID),
    reason=(
        "Live TestRail tests require TESTRAIL_URL, TESTRAIL_EMAIL, TESTRAIL_PASSWORD and "
        "TESTRAIL_PROJECT_ID env vars to be set (TESTRAIL_SUITE_ID too, for multi-suite projects)"
    ),
)


@pytest.fixture(scope="session")
def tr_url() -> str:
    """TestRail server URL, e.g. https://yourcompany.testrail.io"""
    return TESTRAIL_URL


@pytest.fixture(scope="session")
def tr_email() -> str:
    """TestRail account email"""
    return TESTRAIL_EMAIL


@pytest.fixture(scope="session")
def tr_password() -> str:
    """TestRail account password or API key"""
    return TESTRAIL_PASSWORD


@pytest.fixture(scope="session")
def tr_project_id() -> int:
    """TestRail project id used for live tests"""
    return int(TESTRAIL_PROJECT_ID) if TESTRAIL_PROJECT_ID else None


@pytest.fixture(scope="session")
def tr_suite_id():
    """TestRail suite id used for live tests, if project uses suite mode"""
    return int(TESTRAIL_SUITE_ID) if TESTRAIL_SUITE_ID else None


@pytest.fixture(scope="session")
def tr_api(tr_url, tr_email, tr_password):  # pylint: disable=redefined-outer-name
    """Raw TestRailAPI client, for setup/teardown/assertions that sit outside what our engines expose"""
    from testrail_api import TestRailAPI  # pylint: disable=import-outside-toplevel

    return TestRailAPI(tr_url, tr_email, tr_password)
