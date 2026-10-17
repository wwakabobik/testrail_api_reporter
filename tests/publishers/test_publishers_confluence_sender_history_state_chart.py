# -*- coding: utf-8 -*-
"""Tests for confluence_sender module, the ConfluenceSender class, history_state_chart method"""

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


def test_history_state_chart_no_confluence_page(confluence_sender):  # pylint: disable=redefined-outer-name
    """Call history_state_chart without confluence_page should raise ValueError"""
    with pytest.raises(ValueError, match="No confluence page is provided, report aborted!"):
        confluence_sender.history_state_chart(automation_platforms=[{"name": fake.word()}])


def test_history_state_chart_no_automation_platforms(confluence_sender):  # pylint: disable=redefined-outer-name
    """Call history_state_chart without automation_platforms (none set at init either) should raise ValueError"""
    with pytest.raises(ValueError, match="No automation platforms provided, report aborted!"):
        confluence_sender.history_state_chart(confluence_page=fake.word())


def test_history_state_chart_success_with_argument(confluence_sender):  # pylint: disable=redefined-outer-name
    """Call history_state_chart with explicit automation_platforms should draw and attach charts for each"""
    confluence_page = fake.word()
    automation_platforms = [{"name": fake.word()}, {"name": fake.word()}]
    plotly = confluence_sender._ConfluenceSender__plotly  # pylint: disable=protected-access
    confluence = confluence_sender._ConfluenceSender__confluence  # pylint: disable=protected-access
    filenames = [f"{fake.file_name(extension='')}png" for _ in automation_platforms]
    plotly.draw_history_state_chart.side_effect = filenames

    confluence_sender.history_state_chart(confluence_page=confluence_page, automation_platforms=automation_platforms)

    assert plotly.draw_history_state_chart.call_count == len(automation_platforms)
    assert confluence.attach_file.call_count == len(automation_platforms)
    for filename in filenames:
        confluence.attach_file.assert_any_call(filename, page_id=confluence_page, title=filename[:-4])


def test_history_state_chart_success_with_default(confluence_sender):  # pylint: disable=redefined-outer-name
    """Call history_state_chart relying on the instance default automation_platforms"""
    confluence_page = fake.word()
    automation_platforms = [{"name": fake.word()}]
    confluence_sender._ConfluenceSender__automation_platforms = automation_platforms  # pylint: disable=protected-access
    plotly = confluence_sender._ConfluenceSender__plotly  # pylint: disable=protected-access
    filename = f"{fake.file_name(extension='')}png"
    plotly.draw_history_state_chart.return_value = filename

    confluence_sender.history_state_chart(confluence_page=confluence_page)

    plotly.draw_history_state_chart.assert_called_once_with(chart_name=automation_platforms[0]["name"])
