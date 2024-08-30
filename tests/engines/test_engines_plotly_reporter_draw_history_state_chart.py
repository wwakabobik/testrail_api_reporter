# -*- coding: utf-8 -*-
"""Tests for plotly_reporter module, the PlotlyReporter clas, draw_history_state_chart method"""

from os import path, remove, getcwd
from random import choice, randint

import pytest
from faker import Faker


fake = Faker()


def test_draw_history_state_chart_no_chart_name(caplog, random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_history_state_chart without chart_name should raise ValueError

    :param caplog: caplog fixture
    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    with pytest.raises(ValueError, match="No chart name is provided, report aborted!"):
        random_plotly_reporter.draw_history_state_chart()  # type: ignore


def test_draw_history_state_chart_no_filename(caplog, random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_test_case_by_priority without filename should raise ValueError

    :param caplog: caplog fixture
    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    with pytest.raises(ValueError, match="No output filename is provided, report aborted!"):
        random_plotly_reporter.draw_test_case_by_area(cases=[fake.pydict()])
        random_plotly_reporter.draw_history_state_chart()


def test_draw_history_state_chart_creates_file(caplog, random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_history_state_chart with valid parameters should create file

    :param caplog: caplog fixture
    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    raise NotImplementedError


def test_draw_history_state_chart_creates_correct_image(caplog, random_plotly_reporter, compare_image):
    """
    Init PlotlyReporter and call draw_history_state_chart with valid parameters should create valid image

    :param caplog: caplog fixture
    :param random_plotly_reporter: fixture returns PlotlyReporter
    :param compare_image: fixture, returns function to compare images
    """
    raise NotImplementedError


def test_draw_history_state_chart_default_history_data(caplog, random_plotly_reporter, compare_image):
    """
    Init PlotlyReporter and call draw_history_state_chart with default history data

    :param caplog: caplog fixture
    :param random_plotly_reporter: fixture returns PlotlyReporter
    :param compare_image: fixture, returns function to compare images
    """
    raise NotImplementedError


def test_draw_history_state_chart_custom_history_data(caplog, random_plotly_reporter, compare_image):
    """
    Init PlotlyReporter and call draw_history_state_chart with custom history data

    :param caplog: caplog fixture
    :param random_plotly_reporter: fixture returns PlotlyReporter
    :param compare_image: fixture, returns function to compare images
    """
    raise NotImplementedError


def test_draw_history_state_chart_trace1_decor(caplog, random_plotly_reporter, compare_image):
    """
    Init PlotlyReporter and call draw_history_state_chart with custom trace1 decor

    :param caplog: caplog fixture
    :param random_plotly_reporter: fixture returns PlotlyReporter
    :param compare_image: fixture, returns function to compare images
    """
    raise NotImplementedError


def test_draw_history_state_chart_trace2_decor(caplog, random_plotly_reporter, compare_image):
    """
    Init PlotlyReporter and call draw_history_state_chart with custom trace2 decor

    :param caplog: caplog fixture
    :param random_plotly_reporter: fixture returns PlotlyReporter
    :param compare_image: fixture, returns function to compare images
    """
    raise NotImplementedError


def test_draw_history_state_chart_reverse_traces(caplog, random_plotly_reporter, compare_image):
    """
    Init PlotlyReporter and call draw_history_state_chart with reverced traces

    :param caplog: caplog fixture
    :param random_plotly_reporter: fixture returns PlotlyReporter
    :param compare_image: fixture, returns function to compare images
    """
    raise NotImplementedError


def test_draw_history_state_chart_filename_pattern(caplog, random_plotly_reporter, compare_image):
    """
    Init PlotlyReporter and call draw_history_state_chart with reverced traces

    :param caplog: caplog fixture
    :param random_plotly_reporter: fixture returns PlotlyReporter
    :param compare_image: fixture, returns function to compare images
    """
    raise NotImplementedError
