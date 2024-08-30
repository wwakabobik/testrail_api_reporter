# -*- coding: utf-8 -*-
"""Tests for the csv_parser module, 'load_history' function"""

from datetime import datetime

import pytest
from faker import Faker

from testrail_api_reporter.utils.csv_parser import CSVParser  # pylint: disable=import-error,no-name-in-module


fake = Faker()


def test_load_history_data(csv_file, random_stat):
    """Check load_history_data function"""
    parser = CSVParser(filename=csv_file)

    total, automated, not_automated, not_applicable = random_stat
    year = fake.year()
    month = fake.month()
    day_of_month = fake.day_of_month()
    with open(csv_file, "w", encoding="utf-8") as writable_file:
        writable_file.write(f"{year},{month},{day_of_month},{total},{automated},{not_automated},{not_applicable}\n")

    data = parser.load_history_data()

    assert data == [
        [datetime(int(year), int(month), int(day_of_month))],
        [str(total)],
        [str(automated)],
        [str(not_automated)],
        [str(not_applicable)],
    ]


def test_load_history_data_no_filename():
    """No filename is provided for load history"""
    parser = CSVParser()

    with pytest.raises(ValueError):
        parser.load_history_data()


def test_load_history_data_file_not_found():
    """File not found error for load history"""
    parser = CSVParser(filename="non_existent_file.csv")

    with pytest.raises(ValueError):
        parser.load_history_data()
