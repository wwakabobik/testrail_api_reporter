# -*- coding: utf-8 -*-
"""Tests for plotly_reporter module, the PlotlyReporter clas, draw_automation_state_report method"""

from os import path, remove, getcwd
from random import choice

import pytest
from faker import Faker

from testrail_api_reporter.engines.plotly_reporter import (  # pylint: disable=import-error,no-name-in-module
    PlotlyReporter,
)


fake = Faker()


@pytest.fixture
def random_expected_image(case_stat):
    """
    Fixture that chooses random expected image for draw automation state

    :param case_stat: fixture returns empty CaseStat object
    """
    if choice((False, True)):
        case_stat.set_name("Automation State")
        case_stat.total = 5905
        case_stat.automated = 19100
        case_stat.not_automated = 27205
        case_stat.not_applicable = 10092
        return {"filename": f"{getcwd()}/tests/assets/expected_automation_state.png", "data": [case_stat]}
    else:
        case_stat.set_name("Automation State")
        return {"filename": f"{getcwd()}/tests/assets/expected_automation_state_empty.png", "data": [case_stat]}


def test_draw_automation_state_report_no_reports(caplog, random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_automation_state_report without reports should raise ValueError

    :param caplog: caplog fixture
    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    with pytest.raises(ValueError, match="No TestRail reports are provided, report aborted!"):
        random_plotly_reporter.draw_automation_state_report(
            filename=fake.file_name(extension=choice(("png", "jpg", "jpeg", "webp")))
        )


def test_draw_automation_state_report_no_filename(caplog, random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_automation_state_report without filename should raise ValueError

    :param caplog: caplog fixture
    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    with pytest.raises(ValueError, match="No output filename is provided, report aborted!"):
        random_plotly_reporter.draw_automation_state_report(reports=[fake.pydict()])


def test_draw_automation_state_report_creates_file(caplog, case_stat, case_stat_random, random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_automation_state_report with valid parameters should create file

    :param caplog: caplog fixture
    :param case_stat: fixture returns empty CaseStat object
    :param case_stat_random: fixture returns filled with random data CaseStat object
    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    filename = fake.file_name(extension=choice(("png", "jpg", "jpeg", "webp")))
    try:
        reports = [case_stat, case_stat_random]
        random_plotly_reporter.draw_automation_state_report(filename=filename, reports=reports)

        assert path.exists(filename)
    finally:
        if path.exists(filename):
            remove(filename)


def test_draw_automation_state_report_creates_correct_image(caplog, random_expected_image, compare_image):
    """
    Init PlotlyReporter and call draw_automation_state_report with valid parameters should create correct image

    :param caplog: caplog fixture
    :param random_expected_image: fixture, returns any of possible expected cases
    :param compare_image: fixture, returns function to compare images
    """
    type_platforms = [{"name": "Automation State", "sections": [42, 1024, 0]}]
    filename = "actual_automation_state.png"
    try:
        plotly_reporter = PlotlyReporter(type_platforms=type_platforms)
        plotly_reporter.draw_automation_state_report(filename=filename, reports=random_expected_image["data"])
        assert compare_image(actual=filename, expected=random_expected_image["filename"])
    finally:
        if path.exists(filename):
            remove(filename)
