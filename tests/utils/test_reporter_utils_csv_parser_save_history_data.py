# -*- coding: utf-8 -*-
"""Tests for the csv_parser module'"""
from datetime import datetime

import pytest
from faker import Faker

from testrail_api_reporter.utils.csv_parser import CSVParser  # pylint: disable=import-error,no-name-in-module

fake = Faker()


def test_save_history_data(csv_file, random_stat, case_stat):
    """Check save_history_data function"""
    parser = CSVParser(filename=csv_file)

    total, automated, not_automated, not_applicable = random_stat
    case_stat.set_total(total)
    case_stat.set_automated(automated)
    case_stat.set_not_automated(not_automated)
    case_stat.set_not_applicable(not_applicable)

    parser.save_history_data(report=case_stat)

    with open(csv_file, "r", encoding="utf-8") as readable_file:
        data = readable_file.read()
        assert data == (
            f"{datetime.today().strftime('%Y')},"
            f"{datetime.today().strftime('%m')},"
            f"{datetime.today().strftime('%d')},"
            f"{total},{automated},{not_automated},{not_applicable}\n"
        )


def test_save_history_data_no_filename():
    """No filename provided for save history data"""
    parser = CSVParser()

    with pytest.raises(ValueError):
        parser.save_history_data()


def test_save_history_data_no_report(csv_file):
    """No data for save history data"""
    parser = CSVParser(filename=csv_file)

    with pytest.raises(ValueError):
        parser.save_history_data()


def test_save_history_data_already_stored(csv_file, case_stat_random):
    """History already stored for such day for save history data"""
    parser = CSVParser(filename=csv_file)

    parser.save_history_data(report=case_stat_random)
    parser.save_history_data(report=case_stat_random)

    with open(csv_file, "r", encoding="utf-8") as readable_file:
        data = readable_file.read()
        assert data.count("\n") == 1
