# -*- coding: utf-8 -*-
"""Live tests for TestCaseContentGenerator against a real TestRail instance"""

from os import getenv
from uuid import uuid4

import pytest

from testrail_api_reporter.engines.content_generator import (  # pylint: disable=import-error,no-name-in-module
    TestCaseContentGenerator,
)
from testrail_api_reporter.utils.ai_providers import CustomProvider  # pylint: disable=import-error,no-name-in-module

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
def test_update_testrail_case_no_match_queries_live_cases(tr_url, tr_email, tr_password, tr_project_id, tr_suite_id):
    """With an automation_id that can't exist, update should hit the live get_cases endpoint (incl. pagination)
    and cleanly report no match, instead of erroring out"""
    provider = CustomProvider(generate_func=lambda prompt, system_prompt: '{"title": "irrelevant"}')
    generator = TestCaseContentGenerator(
        url=tr_url,
        email=tr_email,
        password=tr_password,
        project_id=tr_project_id,
        suite_id=tr_suite_id,
        provider=provider,
    )

    result = generator.update_testrail_case(
        automation_id=f"live.nonexistent.{uuid4().hex}", content={"title": "irrelevant"}
    )

    assert result is None
