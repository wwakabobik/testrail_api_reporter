# -*- coding: utf-8 -*-
"""Conftest for testsuite"""

from os import path, remove
from random import randint

import pytest
from faker import Faker

from testrail_api_reporter.utils.case_stat import CaseStat  # pylint: disable=import-error,no-name-in-module


@pytest.fixture
def create_test_file() -> str:
    """
    Fixture to create random test file

    :return: filename
    :rtype: str
    """
    test_file = f"not_existing_{Faker().file_name()}"
    with open(test_file, "w", encoding="utf-8") as file:
        file.write("Test")
    assert path.exists(test_file) is True
    yield test_file
    # Cleanup if not removed by tests
    try:
        remove(test_file)
    except FileNotFoundError:
        pass


@pytest.fixture
def random_stat() -> tuple[int, int, int, int]:
    """
    Fixture to return tuple with random statistics

    :return: tuple with random statistics
    :rtype: tuple[int, int, int, int]
    """
    total = randint(0, 32768)
    automated = randint(0, 32768)
    not_automated = randint(0, 32768)
    not_applicable = randint(0, 32768)
    return total, automated, not_automated, not_applicable


@pytest.fixture
def case_stat() -> CaseStat:
    """
    Fixture to return object of CaseStat

    :return: CaseStat
    :rtype: CaseStat
    """
    return CaseStat(Faker().word())


@pytest.fixture
def case_stat_random(case_stat, random_stat):
    """
    Fixture to return object of CaseStat

    :return: CaseStat with random statistics
    :rtype: CaseStat
    """
    total, automated, not_automated, not_applicable = random_stat
    case_stat.set_total(total)
    case_stat.set_automated(automated)
    case_stat.set_not_automated(not_automated)
    case_stat.set_not_applicable(not_applicable)
    return case_stat


@pytest.fixture
def csv_file() -> str:
    """
    Fixture to create random test file

    :return: filename
    """
    test_file = f"not_existing_{Faker().file_name(extension='csv')}"
    with open(test_file, "w", encoding="utf-8") as file:
        file.write("")
    assert path.exists(test_file) is True
    yield test_file
    # Cleanup if not removed by tests
    try:
        remove(test_file)
    except FileNotFoundError:
        pass
