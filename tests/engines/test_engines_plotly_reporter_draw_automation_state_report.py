# -*- coding: utf-8 -*-
"""Tests for plotly_reporter module, the PlotlyReporter clas, draw_automation_state_report method"""

from os import path, remove, getcwd, environ
from random import choice, randint

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
    case_stat.set_name("Automation State")
    return {"filename": f"{getcwd()}/tests/assets/expected_automation_state_empty.png", "data": [case_stat]}


def test_draw_automation_state_report_no_reports(random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_automation_state_report without reports should raise ValueError

    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    with pytest.raises(ValueError, match="No TestRail reports are provided, report aborted!"):
        random_plotly_reporter.draw_automation_state_report(
            filename=fake.file_name(extension=choice(("png", "jpg", "jpeg", "webp")))
        )


def test_draw_automation_state_report_no_filename(random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_automation_state_report without filename should raise ValueError

    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    with pytest.raises(ValueError, match="No output filename is provided, report aborted!"):
        random_plotly_reporter.draw_automation_state_report(reports=[fake.pydict()])


def test_draw_automation_state_report_creates_file(case_stat, case_stat_random, random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_automation_state_report with valid parameters should create file

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


@pytest.mark.xfail(condition="GITHUB_ACTIONS" in environ, reason="Image may differ on GA env")
def test_draw_automation_state_report_creates_correct_image(
    random_expected_image, compare_image  # pylint: disable=W0621
):
    """
    Init PlotlyReporter and call draw_automation_state_report with valid parameters should create correct image

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


def test_draw_automation_state_report_changes_state_markers(
    random_expected_image, compare_image, random_rgb  # pylint: disable=W0621
):
    """
    Init PlotlyReporter and call draw_automation_state_report with state_markers should create different image

    :param random_expected_image: fixture, returns any of possible expected cases
    :param compare_image: fixture, returns function to compare images
    :param random_rgb: fixture, returns random rgb in string format
    """
    type_platforms = [{"name": "Automation State", "sections": [42, 1024, 0]}]
    filename = "actual_automation_state_with_markers.png"
    state_markers = {
        "Automated": {
            "marker": {"color": random_rgb(), "line": {"color": random_rgb(), "width": float(randint(5, 20)) / 10.0}},
            "opacity": float(randint(0, 10)) / 10,
            "textposition": "auto",
        },
        "Not automated": {
            "marker": {"color": random_rgb(), "line": {"color": random_rgb(), "width": float(randint(5, 20)) / 10.0}},
            "opacity": float(randint(0, 10)) / 10,
            "textposition": "auto",
        },
        "N/A": {
            "marker": {"color": random_rgb(), "line": {"color": random_rgb(), "width": float(randint(5, 20)) / 10}},
            "opacity": float(randint(0, 10)) / 10,
            "textposition": "auto",
        },
    }
    try:
        plotly_reporter = PlotlyReporter(type_platforms=type_platforms)
        plotly_reporter.draw_automation_state_report(
            filename=filename, reports=random_expected_image["data"], state_markers=state_markers
        )
        assert not compare_image(actual=filename, expected=random_expected_image["filename"], threshold=1000)
    finally:
        if path.exists(filename):
            remove(filename)
