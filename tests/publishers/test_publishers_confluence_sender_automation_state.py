# -*- coding: utf-8 -*-
"""Tests for confluence_sender module, the ConfluenceSender class, automation_state method"""

from unittest.mock import Mock

import pytest
from faker import Faker

from testrail_api_reporter.publishers.confluence_sender import (  # pylint: disable=import-error,no-name-in-module
    ConfluenceSender,
)

fake = Faker()


@pytest.fixture
def confluence_sender():
    """Fixture to return ConfluenceSender with a mocked Confluence client and plotly engine"""
    plotly_engine = Mock()
    sender = ConfluenceSender(
        url=fake.url(),
        username=fake.email(),
        password=fake.password(),
        type_platforms=[{"name": fake.word(), "sections": [fake.random_int()]}],
        plotly_engine=plotly_engine,
    )
    sender._ConfluenceSender__confluence = Mock()  # pylint: disable=protected-access
    return sender


def test_automation_state_no_confluence_page(confluence_sender):  # pylint: disable=redefined-outer-name
    """Call automation_state without confluence_page should raise ValueError"""
    with pytest.raises(ValueError, match="No confluence page is provided, report aborted!"):
        confluence_sender.automation_state(reports=[Mock()])


def test_automation_state_no_reports(confluence_sender):  # pylint: disable=redefined-outer-name
    """Call automation_state without reports should raise ValueError"""
    with pytest.raises(ValueError, match="No TestRail reports are provided, report aborted!"):
        confluence_sender.automation_state(confluence_page=fake.word())


def test_automation_state_success(confluence_sender):  # pylint: disable=redefined-outer-name
    """Call automation_state with valid parameters should draw the chart and attach it to Confluence"""
    confluence_page = fake.word()
    reports = [Mock()]
    filename = fake.file_name(extension="png")

    confluence_sender.automation_state(confluence_page=confluence_page, reports=reports, filename=filename)

    plotly = confluence_sender._ConfluenceSender__plotly  # pylint: disable=protected-access
    confluence = confluence_sender._ConfluenceSender__confluence  # pylint: disable=protected-access
    plotly.draw_automation_state_report.assert_called_once_with(reports=reports, filename=filename)
    confluence.attach_file.assert_called_once_with(filename, page_id=confluence_page, title="current_automation")
