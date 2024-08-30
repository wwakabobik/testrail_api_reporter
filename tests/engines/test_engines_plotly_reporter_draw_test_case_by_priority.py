# -*- coding: utf-8 -*-
"""Tests for plotly_reporter module, the PlotlyReporter clas, draw_test_case_by_priority method"""

from os import path, remove, getcwd
from random import choice, randint

import pytest
from faker import Faker


fake = Faker()


def test_draw_test_case_by_priority_no_cases(caplog, random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_test_case_by_priority without cases should raise ValueError

    :param caplog: caplog fixture
    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    with pytest.raises(ValueError, match="No TestRail values are provided, report aborted!"):
        random_plotly_reporter.draw_test_case_by_priority(
            filename=fake.file_name(extension=choice(("png", "jpg", "jpeg", "webp")))
        )


def test_draw_test_case_by_priority_no_filename(caplog, random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_test_case_by_priority without filename should raise ValueError

    :param caplog: caplog fixture
    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    with pytest.raises(ValueError, match="No output filename is provided, report aborted!"):
        random_plotly_reporter.draw_test_case_by_priority(values=[fake.pydict()])


def test_draw_test_case_by_priority_creates_file(caplog, random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_test_case_by_priority with valid parameters should create file

    :param caplog: caplog fixture
    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    filename = fake.file_name(extension=choice(("png", "jpg", "jpeg", "webp")))
    try:
        random_plotly_reporter.draw_test_case_by_priority(
            filename=filename, values=[randint(0, 1024) for _ in range(randint(1, 4))]
        )

        assert path.exists(filename)
    finally:
        if path.exists(filename):
            remove(filename)


def test_draw_test_case_by_priority_creates_correct_image(caplog, compare_image, random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_test_case_by_priority with valid parameters should create correct image

    :param caplog: caplog fixture
    :param compare_image: fixture, returns function to compare images
    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    filename = "actual_test_case_by_priority.png"
    try:
        random_plotly_reporter.draw_test_case_by_priority(filename=filename, values=[1, 101, 72, 16])
        assert compare_image(actual=filename, expected=f"{getcwd()}/tests/assets/expected_case_by_priority.png")
    finally:
        if path.exists(filename):
            remove(filename)


def test_draw_test_case_by_priority_creates_change_lines(caplog, compare_image, random_plotly_reporter, random_rgb):
    """
    Init PlotlyReporter and call draw_test_case_by_priority with custom lines

    :param caplog: caplog fixture
    :param compare_image: fixture, returns function to compare images
    :param random_plotly_reporter: fixture returns PlotlyReporter
    :param random_rgb: fixture, returns random rgb in string format
    """
    filename = "actual_test_case_by_priority_lines.png"
    try:
        lines = {"color": random_rgb(), "width": float(randint(6, 50)) / 10.0}
        random_plotly_reporter.draw_test_case_by_priority(filename=filename, values=[1, 101, 72, 16], lines=lines)
        assert not compare_image(actual=filename, expected=f"{getcwd()}/tests/assets/expected_case_by_priority.png")
    finally:
        if path.exists(filename):
            remove(filename)


def test_draw_test_case_by_priority_creates_change_labels(caplog, compare_image, random_plotly_reporter):
    """
    Init PlotlyReporter and call draw_test_case_by_priority with custom labels

    :param caplog: caplog fixture
    :param compare_image: fixture, returns function to compare images
    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    filename = "actual_test_case_by_priority_labels.png"
    labels = [fake.name() for _ in range(randint(1, 10))]
    try:
        random_plotly_reporter.draw_test_case_by_priority(filename=filename, values=[1, 101, 72, 16], pr_labels=labels)
        assert not compare_image(actual=filename, expected=f"{getcwd()}/tests/assets/expected_case_by_priority.png")
    finally:
        if path.exists(filename):
            remove(filename)


def test_draw_test_case_by_priority_creates_change_colors(caplog, compare_image, random_plotly_reporter, random_rgb):
    """
    Init PlotlyReporter and call draw_test_case_by_priority with custom labels

    :param caplog: caplog fixture
    :param compare_image: fixture, returns function to compare images
    :param random_plotly_reporter: fixture returns PlotlyReporter
    """
    filename = "actual_test_case_by_priority_colors.png"
    colors = [random_rgb() for _ in range(randint(1, 10))]
    try:
        random_plotly_reporter.draw_test_case_by_priority(filename=filename, values=[1, 101, 72, 16], pr_colors=colors)
        assert not compare_image(actual=filename, expected=f"{getcwd()}/tests/assets/expected_case_by_priority.png")
    finally:
        if path.exists(filename):
            remove(filename)
