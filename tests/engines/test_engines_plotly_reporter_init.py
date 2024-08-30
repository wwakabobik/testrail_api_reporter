# -*- coding: utf-8 -*-
"""Tests for plotly_reporter module, the PlotlyReporter class, init method"""

from logging import getLogger, INFO, WARNING, ERROR, FATAL
from os import path, remove
from random import randint, choice

import pytest
from faker import Faker

from testrail_api_reporter.engines.plotly_reporter import (  # pylint: disable=import-error,no-name-in-module
    PlotlyReporter,
)
from testrail_api_reporter.utils.logger_config import (  # pylint: disable=import-error,no-name-in-module
    setup_logger,
    DEFAULT_LOGGING_LEVEL,
)

fake = Faker()


def test_plotly_reporter_init_default_params():
    """Init PlotlyReporter with default parameters"""
    type_platforms = [{"name": fake.word(), "sections": [randint(1, 10000)]} for _ in range(randint(1, 5))]

    plotly_reporter = PlotlyReporter(type_platforms=type_platforms)

    logger = getLogger("PlotlyReporter")
    assert logger.level == DEFAULT_LOGGING_LEVEL
    assert path.exists("PlotlyReporter.log")

    attributes = vars(plotly_reporter)
    assert attributes["_PlotlyReporter__pr_labels"] == ["Low", "Medium", "High", "Critical"]
    assert attributes["_PlotlyReporter__pr_colors"] == [
        "rgb(173,216,230)",
        "rgb(34,139,34)",
        "rgb(255,255,51)",
        "rgb(255, 153, 153)",
    ]
    assert attributes["_PlotlyReporter__ar_colors"] == [
        "rgb(255, 153, 153)",
        "rgb(255,255,51)",
        "rgb(34,139,34)",
        "rgb(173,216,230)",
        "rgb(65,105,225)",
        "rgb(192, 192, 192)",
    ]
    assert attributes["_PlotlyReporter__lines"] == {"color": "rgb(0,0,51)", "width": 1.5}
    assert attributes["_PlotlyReporter__type_platforms"] == type_platforms


def test_plotly_reporter_init_custom_params():
    """Init PlotlyReporter with custom parameters"""
    logger_file = fake.file_name(extension="log")
    logger_name = fake.name()
    logger_level = choice((INFO, WARNING, ERROR, FATAL))
    try:
        logger = setup_logger(logger_name, logger_file, level=logger_level)
        type_platforms = [{"name": fake.word(), "sections": [randint(1, 10000)]} for _ in range(randint(1, 5))]
        pr_labels = [fake.word() for _ in range(4)]
        pr_colors = [f"rgb({randint(0, 255)},{randint(0, 255)},{randint(0, 255)})" for _ in range(4)]
        ar_colors = [f"rgb({randint(0, 255)},{randint(0, 255)},{randint(0, 255)})" for _ in range(6)]
        lines = {"color": f"rgb({randint(0, 255)},{randint(0, 255)},{randint(0, 255)})", "width": randint(1, 3)}

        plotly_reporter = PlotlyReporter(
            pr_colors=pr_colors,
            pr_labels=pr_labels,
            ar_colors=ar_colors,
            lines=lines,
            type_platforms=type_platforms,
            logger=logger,
            log_level=INFO,
        )

        logger = getLogger(logger_name)
        assert logger.level == logger_level
        assert path.exists(logger_file)

        attributes = vars(plotly_reporter)
        assert attributes["_PlotlyReporter__pr_labels"] == pr_labels
        assert attributes["_PlotlyReporter__pr_colors"] == pr_colors
        assert attributes["_PlotlyReporter__ar_colors"] == ar_colors
        assert attributes["_PlotlyReporter__lines"] == lines
        assert attributes["_PlotlyReporter__type_platforms"] == type_platforms
    finally:
        if path.exists(logger_file):
            remove(logger_file)


def test_plotly_reporter_init_no_type_platforms():
    """Init PlotlyReporter without type_platforms should raise ValueError"""
    with pytest.raises(ValueError, match="Platform types is not provided, Plotly Reporter cannot be initialized!"):
        PlotlyReporter()
