# -*- coding: utf-8 -*-
"""Tests for confluence_sender module, the ConfluenceSender class, history_type_chart method"""

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


def test_history_type_chart_no_confluence_page(confluence_sender):  # pylint: disable=redefined-outer-name
    """Call history_type_chart without confluence_page should raise ValueError"""
    with pytest.raises(ValueError, match="No confluence page is provided, report aborted!"):
        confluence_sender.history_type_chart(type_platforms=[{"name": fake.word()}])


def test_history_type_chart_no_type_platforms(confluence_sender):  # pylint: disable=redefined-outer-name
    """Call history_type_chart without type_platforms should raise ValueError (none set at init either)"""
    confluence_sender._ConfluenceSender__type_platforms = None  # pylint: disable=protected-access
    with pytest.raises(ValueError, match="No type platforms specified, report aborted!"):
        confluence_sender.history_type_chart(confluence_page=fake.word())


def test_history_type_chart_success_with_argument(confluence_sender):  # pylint: disable=redefined-outer-name
    """Call history_type_chart with explicit type_platforms should draw and attach the chart"""
    confluence_page = fake.word()
    type_platforms = [{"name": fake.word()}]
    filename = fake.file_name(extension="png")

    confluence_sender.history_type_chart(
        confluence_page=confluence_page, type_platforms=type_platforms, filename=filename
    )

    plotly = confluence_sender._ConfluenceSender__plotly  # pylint: disable=protected-access
    confluence = confluence_sender._ConfluenceSender__confluence  # pylint: disable=protected-access
    plotly.draw_history_type_chart.assert_called_once_with(type_platforms=type_platforms, filename=filename)
    confluence.attach_file.assert_called_once_with(
        filename, page_id=confluence_page, title="current_area_distribution_history"
    )


def test_history_type_chart_success_with_default(confluence_sender):  # pylint: disable=redefined-outer-name
    """Call history_type_chart relying on the instance default type_platforms"""
    confluence_page = fake.word()

    confluence_sender.history_type_chart(confluence_page=confluence_page)

    plotly = confluence_sender._ConfluenceSender__plotly  # pylint: disable=protected-access
    type_platforms = confluence_sender._ConfluenceSender__type_platforms  # pylint: disable=protected-access
    plotly.draw_history_type_chart.assert_called_once_with(
        type_platforms=type_platforms, filename="current_area_distribution_history.png"
    )
