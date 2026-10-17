# -*- coding: utf-8 -*-
"""Tests for plotly_reporter module, the PlotlyReporter clas, draw_history_type_chart method"""

from os import path, remove
from random import randint

import pytest
from faker import Faker

fake = Faker()


def _write_history_csv(filename):
    """Write a minimal single-row history CSV file at the given path"""
    with open(filename, "w", encoding="utf-8") as writable_file:
        writable_file.write(f"2024,1,1,{randint(1, 100)},{randint(0, 100)},0,0\n")


def test_draw_history_type_chart_no_filename(random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_history_type_chart without filename should raise ValueError

    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    with pytest.raises(ValueError, match="No output filename is provided, report aborted!"):
        random_plotly_reporter.draw_history_type_chart()


def test_draw_history_type_chart_creates_file(random_plotly_reporter, random_type_platforms):
    """
    Init PlotlyReporter and call draw_history_type_chart with default (instance) type_platforms should create file

    :param random_plotly_reporter: fixture returns PlotlyReporter
    :param random_type_platforms: fixture returns the same type_platforms used to build random_plotly_reporter
    """
    filename = fake.file_name(extension="png")
    csv_files = [f"current_area_distribution_{platform['name']}.csv" for platform in random_type_platforms]
    try:
        for csv_file in csv_files:
            _write_history_csv(csv_file)
        random_plotly_reporter.draw_history_type_chart(filename=filename)
        assert path.exists(filename)
    finally:
        if path.exists(filename):
            remove(filename)
        for csv_file in csv_files:
            if path.exists(csv_file):
                remove(csv_file)


def test_draw_history_type_chart_custom_type_platforms(random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_history_type_chart with custom type_platforms

    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    filename = fake.file_name(extension="png")
    type_platforms = [{"name": fake.word(), "sections": [randint(1, 10000)]} for _ in range(randint(1, 3))]
    csv_files = [f"current_area_distribution_{platform['name']}.csv" for platform in type_platforms]
    try:
        for csv_file in csv_files:
            _write_history_csv(csv_file)
        random_plotly_reporter.draw_history_type_chart(filename=filename, type_platforms=type_platforms)
        assert path.exists(filename)
    finally:
        if path.exists(filename):
            remove(filename)
        for csv_file in csv_files:
            if path.exists(csv_file):
                remove(csv_file)


def test_draw_history_type_chart_empty_type_platforms(random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_history_type_chart with an empty type_platforms list should create file
    without any data traces

    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    filename = fake.file_name(extension="png")
    # An empty type_platforms argument falls back to the instance default (required non-empty at init time),
    # so the only way to exercise the zero-iteration branch of the loop is via the instance attribute itself.
    random_plotly_reporter._PlotlyReporter__type_platforms = []  # pylint: disable=protected-access
    try:
        random_plotly_reporter.draw_history_type_chart(filename=filename)
        assert path.exists(filename)
    finally:
        if path.exists(filename):
            remove(filename)


def test_draw_history_type_chart_custom_ar_colors(random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_history_type_chart with custom ar_colors

    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    filename = fake.file_name(extension="png")
    type_platforms = [{"name": fake.word(), "sections": [randint(1, 10000)]}]
    ar_colors = [f"rgb({randint(0, 255)},{randint(0, 255)},{randint(0, 255)})"]
    csv_file = f"current_area_distribution_{type_platforms[0]['name']}.csv"
    try:
        _write_history_csv(csv_file)
        random_plotly_reporter.draw_history_type_chart(
            filename=filename, type_platforms=type_platforms, ar_colors=ar_colors
        )
        assert path.exists(filename)
    finally:
        if path.exists(filename):
            remove(filename)
        if path.exists(csv_file):
            remove(csv_file)


def test_draw_history_type_chart_custom_lines(random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_history_type_chart with custom lines

    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    filename = fake.file_name(extension="png")
    type_platforms = [{"name": fake.word(), "sections": [randint(1, 10000)]}]
    lines = {"color": f"rgb({randint(0, 255)},{randint(0, 255)},{randint(0, 255)})", "width": randint(1, 3)}
    csv_file = f"current_area_distribution_{type_platforms[0]['name']}.csv"
    try:
        _write_history_csv(csv_file)
        random_plotly_reporter.draw_history_type_chart(filename=filename, type_platforms=type_platforms, lines=lines)
        assert path.exists(filename)
    finally:
        if path.exists(filename):
            remove(filename)
        if path.exists(csv_file):
            remove(csv_file)


def test_draw_history_type_chart_custom_filename_pattern(random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_history_type_chart with custom history_filename_pattern

    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    filename = fake.file_name(extension="png")
    type_platforms = [{"name": fake.word(), "sections": [randint(1, 10000)]}]
    history_filename_pattern = fake.word()
    csv_file = f"{history_filename_pattern}_{type_platforms[0]['name']}.csv"
    try:
        _write_history_csv(csv_file)
        random_plotly_reporter.draw_history_type_chart(
            filename=filename, type_platforms=type_platforms, history_filename_pattern=history_filename_pattern
        )
        assert path.exists(filename)
    finally:
        if path.exists(filename):
            remove(filename)
        if path.exists(csv_file):
            remove(csv_file)
