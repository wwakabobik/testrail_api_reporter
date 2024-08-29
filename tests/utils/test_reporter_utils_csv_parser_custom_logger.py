# -*- coding: utf-8 -*-
"""Tests for the csv_parser module against custom logger"""

from logging import Logger, DEBUG, ERROR, FATAL, INFO, WARNING
from random import choice

from faker import Faker

from testrail_api_reporter.utils.csv_parser import CSVParser  # pylint: disable=import-error,no-name-in-module


fake = Faker()


def test_custom_csv_logger():
    """Use custom logger"""
    CSVParser(logger=Logger(name=fake.name(), level=choice((DEBUG, INFO, WARNING, ERROR, FATAL))))
