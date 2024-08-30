# -*- coding: utf-8 -*-
"""Tests for plotly_reporter module, the PlotlyReporter clas, draw_test_case_by_area method"""

from copy import deepcopy
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
        case_stat_first = case_stat
        case_stat_first.set_name("UI")
        case_stat_first.total = 999
        case_stat_first.automated = 1234
        case_stat_first.not_automated = 99
        case_stat_first.not_applicable = 56
        case_stat_second = deepcopy(case_stat)
        case_stat_second.set_name("API")
        case_stat_second.total = 77
        case_stat_second.automated = 11
        case_stat_second.not_automated = 0
        case_stat_second.not_applicable = 1024
        return {
            "filename": f"{getcwd()}/tests/assets/expected_case_by_area.png",
            "data": [case_stat_first, case_stat_second],
        }
    else:
        case_stat.set_name("Automation State")
        return {"filename": f"{getcwd()}/tests/assets/expected_case_by_area_empty.png", "data": [case_stat]}


def test_draw_test_case_by_area_no_cases(caplog, random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_test_case_by_area without cases should raise ValueError

    :param caplog: caplog fixture
    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    with pytest.raises(ValueError, match="No TestRail cases are provided, report aborted!"):
        random_plotly_reporter.draw_test_case_by_area(
            filename=fake.file_name(extension=choice(("png", "jpg", "jpeg", "webp")))
        )


def test_draw_test_case_by_area_no_filename(caplog, random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_test_case_by_area without filename should raise ValueError

    :param caplog: caplog fixture
    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    with pytest.raises(ValueError, match="No output filename is provided, report aborted!"):
        random_plotly_reporter.draw_test_case_by_area(cases=[fake.pydict()])


def test_draw_test_case_by_area_creates_file(caplog, case_stat, case_stat_random, random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_test_case_by_area with valid parameters should create file

    :param caplog: caplog fixture
    :param case_stat: fixture returns empty CaseStat object
    :param case_stat_random: fixture returns filled with random data CaseStat object
    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    filename = fake.file_name(extension=choice(("png", "jpg", "jpeg", "webp")))
    try:
        cases = [case_stat_random, case_stat]

        random_plotly_reporter.draw_test_case_by_area(filename=filename, cases=cases)

        assert path.exists(filename)
    finally:
        if path.exists(filename):
            remove(filename)


def test_draw_test_case_by_area_creates_correct_image(caplog, random_expected_image, compare_image):
    """
    Init PlotlyReporter and call draw_test_case_by_area with valid parameters should create correct image

    :param caplog: caplog fixture
    :param random_expected_image: fixture, returns any of possible expected cases
    :param compare_image: fixture, returns function to compare images
    """
    type_platforms = [{"name": "UI", "sections": [8080, 11, 4]}, {"name": "API", "sections": [12, 101, 86]}]
    filename = "actual_test_case_by_area.png"
    try:
        plotly_reporter = PlotlyReporter(type_platforms=type_platforms)
        plotly_reporter.draw_test_case_by_area(filename=filename, cases=random_expected_image["data"])
        assert compare_image(actual=filename, expected=random_expected_image["filename"])
    finally:
        if path.exists(filename):
            remove(filename)
