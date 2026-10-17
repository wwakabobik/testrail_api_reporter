# -*- coding: utf-8 -*-
"""Tests for plotly_reporter module, the PlotlyReporter clas, draw_history_state_chart method"""

from datetime import datetime
from os import environ, getcwd, path, remove

import pytest
from faker import Faker


fake = Faker()


HISTORY_DATA = [
    [datetime(2024, 1, 1), datetime(2024, 1, 2), datetime(2024, 1, 3)],
    ["10", "20", "30"],
    ["5", "15", "25"],
    ["0", "0", "0"],
    ["5", "5", "5"],
]


def test_draw_history_state_chart_no_chart_name(random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_history_state_chart without chart_name should raise ValueError

    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    with pytest.raises(ValueError, match="No chart name is provided, report aborted!"):
        random_plotly_reporter.draw_history_state_chart()  # type: ignore


def test_draw_history_state_chart_no_filename(random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_test_case_by_priority without filename should raise ValueError

    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    fake_name = fake.name()
    match = f"Can't open report file 'current_automation_{fake_name.replace(' ', '_')}.csv', load history data aborted!"
    with pytest.raises(ValueError, match=match):
        random_plotly_reporter.draw_history_state_chart(chart_name=fake_name)


def test_draw_history_state_chart_creates_file(random_plotly_reporter):
    """Init PlotlyReporter and call draw_history_state_chart with valid parameters should create file"""
    filename = fake.file_name(extension="png")
    try:
        random_plotly_reporter.draw_history_state_chart(
            chart_name=fake.name(), history_data=HISTORY_DATA, filename=filename
        )
        assert path.exists(filename)
    finally:
        if path.exists(filename):
            remove(filename)


@pytest.mark.xfail(condition="GITHUB_ACTIONS" in environ, reason="Image may differ on GA env")
def test_draw_history_state_chart_creates_correct_image(random_plotly_reporter, compare_image):
    """Init PlotlyReporter and call draw_history_state_chart with valid parameters should create valid image"""
    filename = "actual_history_state_chart.png"
    try:
        random_plotly_reporter.draw_history_state_chart(
            chart_name=fake.name(), history_data=HISTORY_DATA, filename=filename
        )
        assert compare_image(actual=filename, expected=f"{getcwd()}/tests/assets/expected_history_state_chart.png")
    finally:
        if path.exists(filename):
            remove(filename)


def test_draw_history_state_chart_default_history_data(random_plotly_reporter):
    """Init PlotlyReporter and call draw_history_state_chart with default history data"""
    chart_name = fake.name()
    csv_filename = f"current_automation_{chart_name.replace(' ', '_')}.csv"
    png_filename = f"current_automation_{chart_name.replace(' ', '_')}.png"
    try:
        with open(csv_filename, "w", encoding="utf-8") as writable_file:
            writable_file.write("2024,1,1,10,5,0,5\n")
        result = random_plotly_reporter.draw_history_state_chart(chart_name=chart_name)
        assert result == png_filename
        assert path.exists(png_filename)
    finally:
        if path.exists(csv_filename):
            remove(csv_filename)
        if path.exists(png_filename):
            remove(png_filename)


def test_draw_history_state_chart_custom_history_data(random_plotly_reporter):
    """Init PlotlyReporter and call draw_history_state_chart with custom history data"""
    filename = fake.file_name(extension="png")
    try:
        result = random_plotly_reporter.draw_history_state_chart(
            chart_name=fake.name(), history_data=HISTORY_DATA, filename=filename
        )
        assert result == filename
        assert path.exists(filename)
    finally:
        if path.exists(filename):
            remove(filename)


def test_draw_history_state_chart_trace1_decor(random_plotly_reporter, random_rgb):
    """Init PlotlyReporter and call draw_history_state_chart with custom trace1 decor"""
    filename = fake.file_name(extension="png")
    try:
        trace1_decor = {"fill": "tonexty", "line": {"width": 1.0, "color": random_rgb()}, "mode": "none"}
        random_plotly_reporter.draw_history_state_chart(
            chart_name=fake.name(), history_data=HISTORY_DATA, filename=filename, trace1_decor=trace1_decor
        )
        assert path.exists(filename)
    finally:
        if path.exists(filename):
            remove(filename)


def test_draw_history_state_chart_trace2_decor(random_plotly_reporter, random_rgb):
    """Init PlotlyReporter and call draw_history_state_chart with custom trace2 decor"""
    filename = fake.file_name(extension="png")
    try:
        trace2_decor = {"fill": "tozeroy", "line": {"width": 1.0, "color": random_rgb()}, "mode": "none"}
        random_plotly_reporter.draw_history_state_chart(
            chart_name=fake.name(), history_data=HISTORY_DATA, filename=filename, trace2_decor=trace2_decor
        )
        assert path.exists(filename)
    finally:
        if path.exists(filename):
            remove(filename)


def test_draw_history_state_chart_reverse_traces(random_plotly_reporter):
    """Init PlotlyReporter and call draw_history_state_chart with reversed traces"""
    filename = fake.file_name(extension="png")
    try:
        random_plotly_reporter.draw_history_state_chart(
            chart_name=fake.name(), history_data=HISTORY_DATA, filename=filename, reverse_traces=True
        )
        assert path.exists(filename)
    finally:
        if path.exists(filename):
            remove(filename)


def test_draw_history_state_chart_filename_pattern(random_plotly_reporter):
    """Init PlotlyReporter and call draw_history_state_chart with filename pattern"""
    chart_name = fake.name()
    filename_pattern = fake.word()
    csv_filename = f"{filename_pattern}_{chart_name.replace(' ', '_')}.csv"
    png_filename = f"{filename_pattern}_{chart_name.replace(' ', '_')}.png"
    try:
        with open(csv_filename, "w", encoding="utf-8") as writable_file:
            writable_file.write("2024,1,1,10,5,0,5\n")
        result = random_plotly_reporter.draw_history_state_chart(
            chart_name=chart_name, filename_pattern=filename_pattern
        )
        assert result == png_filename
        assert path.exists(png_filename)
    finally:
        if path.exists(csv_filename):
            remove(csv_filename)
        if path.exists(png_filename):
            remove(png_filename)
