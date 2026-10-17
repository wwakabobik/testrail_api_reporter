# -*- coding: utf-8 -*-
"""Tests for confluence_sender module, the ConfluenceSender class, test_case_area_distribution method"""

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


def test_test_case_area_distribution_no_confluence_page(confluence_sender):  # pylint: disable=redefined-outer-name
    """Call test_case_area_distribution without confluence_page should raise ValueError"""
    with pytest.raises(ValueError, match="No confluence page is provided, report aborted!"):
        confluence_sender.test_case_area_distribution(cases=[Mock()])


def test_test_case_area_distribution_no_cases(confluence_sender):  # pylint: disable=redefined-outer-name
    """Call test_case_area_distribution without cases should raise ValueError"""
    with pytest.raises(ValueError, match="No TestRail cases are provided, report aborted!"):
        confluence_sender.test_case_area_distribution(confluence_page=fake.word())


def test_test_case_area_distribution_success(confluence_sender):  # pylint: disable=redefined-outer-name
    """Call test_case_area_distribution with valid parameters should draw and attach the chart"""
    confluence_page = fake.word()
    cases = [Mock()]
    filename = fake.file_name(extension="png")

    confluence_sender.test_case_area_distribution(confluence_page=confluence_page, cases=cases, filename=filename)

    plotly = confluence_sender._ConfluenceSender__plotly  # pylint: disable=protected-access
    confluence = confluence_sender._ConfluenceSender__confluence  # pylint: disable=protected-access
    plotly.draw_test_case_by_area.assert_called_once_with(cases=cases, filename=filename)
    confluence.attach_file.assert_called_once_with(
        filename, page_id=confluence_page, title="current_area_distribution"
    )
