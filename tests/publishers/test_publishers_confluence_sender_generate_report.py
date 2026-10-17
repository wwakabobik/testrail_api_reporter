# -*- coding: utf-8 -*-
"""Tests for confluence_sender module, the ConfluenceSender class, generate_report method"""

from unittest.mock import Mock, patch

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


def test_generate_report_no_confluence_page(confluence_sender):  # pylint: disable=redefined-outer-name
    """Call generate_report without confluence_page (and none set at init) should raise ValueError"""
    with pytest.raises(ValueError, match="No confluence page is provided, report aborted!"):
        confluence_sender.generate_report(reports=[Mock()], cases=[Mock()], values=[1])


def test_generate_report_no_reports(confluence_sender):  # pylint: disable=redefined-outer-name
    """Call generate_report without reports should raise ValueError"""
    with pytest.raises(ValueError, match="No TestRail reports are provided, report aborted!"):
        confluence_sender.generate_report(confluence_page=fake.word(), cases=[Mock()], values=[1])


def test_generate_report_no_cases(confluence_sender):  # pylint: disable=redefined-outer-name
    """Call generate_report without cases should raise ValueError"""
    with pytest.raises(ValueError, match="No TestRail cases are provided, report aborted!"):
        confluence_sender.generate_report(confluence_page=fake.word(), reports=[Mock()], values=[1])


def test_generate_report_no_values(confluence_sender):  # pylint: disable=redefined-outer-name
    """Call generate_report without values should raise ValueError"""
    with pytest.raises(ValueError, match="No TestRail values are provided, report aborted!"):
        confluence_sender.generate_report(confluence_page=fake.word(), reports=[Mock()], cases=[Mock()])


def test_generate_report_no_type_platforms(confluence_sender):  # pylint: disable=redefined-outer-name
    """Call generate_report without type_platforms (and none set at init) should raise ValueError"""
    confluence_sender._ConfluenceSender__type_platforms = None  # pylint: disable=protected-access
    with pytest.raises(ValueError, match="No type platforms specified, report aborted!"):
        confluence_sender.generate_report(confluence_page=fake.word(), reports=[Mock()], cases=[Mock()], values=[1])


def test_generate_report_no_automation_platforms(confluence_sender):  # pylint: disable=redefined-outer-name
    """Call generate_report without automation_platforms (and none set at init) should raise ValueError"""
    with pytest.raises(ValueError, match="No type platforms specified, report aborted!"):
        confluence_sender.generate_report(confluence_page=fake.word(), reports=[Mock()], cases=[Mock()], values=[1])


def test_generate_report_success_with_arguments(confluence_sender):  # pylint: disable=redefined-outer-name
    """Call generate_report with every argument provided should delegate to each sub-report method"""
    confluence_page = fake.word()
    reports = [Mock()]
    cases = [Mock()]
    values = [1, 2]
    type_platforms = [{"name": fake.word()}]
    automation_platforms = [{"name": fake.word()}]

    with patch.object(confluence_sender, "automation_state") as mock_automation_state, patch.object(
        confluence_sender, "test_case_priority_distribution"
    ) as mock_priority, patch.object(confluence_sender, "test_case_area_distribution") as mock_area, patch.object(
        confluence_sender, "history_type_chart"
    ) as mock_type_chart, patch.object(
        confluence_sender, "history_state_chart"
    ) as mock_state_chart:
        confluence_sender.generate_report(
            confluence_page=confluence_page,
            reports=reports,
            cases=cases,
            values=values,
            type_platforms=type_platforms,
            automation_platforms=automation_platforms,
        )

    mock_automation_state.assert_called_once_with(confluence_page=confluence_page, reports=reports)
    mock_priority.assert_called_once_with(confluence_page=confluence_page, values=values)
    mock_area.assert_called_once_with(confluence_page=confluence_page, cases=cases)
    mock_type_chart.assert_called_once_with(confluence_page=confluence_page)
    mock_state_chart.assert_called_once_with(confluence_page=confluence_page)


def test_generate_report_success_with_defaults(confluence_sender):  # pylint: disable=redefined-outer-name
    """Call generate_report relying on instance defaults for confluence_page/type_platforms/automation_platforms"""
    confluence_page = fake.word()
    automation_platforms = [{"name": fake.word()}]
    confluence_sender._ConfluenceSender__confluence_page = confluence_page  # pylint: disable=protected-access
    confluence_sender._ConfluenceSender__automation_platforms = automation_platforms  # pylint: disable=protected-access

    with patch.object(confluence_sender, "automation_state") as mock_automation_state, patch.object(
        confluence_sender, "test_case_priority_distribution"
    ), patch.object(confluence_sender, "test_case_area_distribution"), patch.object(
        confluence_sender, "history_type_chart"
    ) as mock_type_chart, patch.object(
        confluence_sender, "history_state_chart"
    ):
        confluence_sender.generate_report(reports=[Mock()], cases=[Mock()], values=[1])

    mock_automation_state.assert_called_once()
    assert mock_automation_state.call_args.kwargs["confluence_page"] == confluence_page
    mock_type_chart.assert_called_once_with(confluence_page=confluence_page)
