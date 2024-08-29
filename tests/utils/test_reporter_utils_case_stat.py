# -*- coding: utf-8 -*-
"""Tests for the reporter_utils module, сlass 'CaseStat'"""

import pytest
from faker import Faker

from testrail_api_reporter.utils.case_stat import CaseStat  # pylint: disable=import-error,no-name-in-module

fake = Faker()


def test_case_stat_init():
    name = fake.word()
    case_stat = CaseStat(name)
    assert case_stat.name == name
    assert case_stat.name == name
    assert case_stat.total == 0
    assert case_stat.automated == 0
    assert case_stat.not_automated == 0
    assert case_stat.not_applicable == 0

def test_case_stat_name():
    """Check name attribute"""
    name = fake.word()
    case_stat = CaseStat(name)

    assert case_stat.get_name() == name, "Test case name does not match"

    new_name = fake.word()
    case_stat.set_name(new_name)
    assert case_stat.get_name() == new_name, "Test case name does not match after change"

def test_case_stat_total():
    """Check total"""
    name = fake.word()
    case_stat = CaseStat(name)

    total = fake.random_number()
    case_stat.set_total(total)
    assert case_stat.get_total() == total, "Total number of test cases does not match"

def test_case_stat_automated():
    """Check automated"""
    name = fake.word()
    case_stat = CaseStat(name)

    automated = fake.random_number()
    case_stat.set_automated(automated)
    assert case_stat.get_automated() == automated, "Number of automated test cases does not match"

def test_case_stat_not_automated():
    """Check not automated"""
    name = fake.word()
    case_stat = CaseStat(name)

    not_automated = fake.random_number()
    case_stat.set_not_automated(not_automated)
    assert case_stat.get_not_automated() == not_automated, "Number of not automated test cases does not match"

def test_case_stat_not_applicable():
    """Check not applicable"""
    name = fake.word()
    case_stat = CaseStat(name)

    not_applicable = fake.random_number()
    case_stat.set_not_applicable(not_applicable)
    assert case_stat.get_not_applicable() == not_applicable, "Number of not applicable test cases does not match"


def test_case_stat_negative():
    # Создаем экземпляр клас��а с именем теста
    name = fake.word()
    case_stat = CaseStat(name)

    # Пытаемся установить отрицательное количество тестов
    with pytest.raises(ValueError):
        case_stat.set_total(-1)

    # Пытаемся установить количество тестов не числовым значением
    with pytest.raises(TypeError):
        case_stat.set_total("not a number")

    # Повторяем для остальных сеттеров
    with pytest.raises(ValueError):
        case_stat.set_automated(-1)

    with pytest.raises(TypeError):
        case_stat.set_automated("not a number")

    with pytest.raises(ValueError):
        case_stat.set_not_automated(-1)

    with pytest.raises(TypeError):
        case_stat.set_not_automated("not a number")

    with pytest.raises(ValueError):
        case_stat.set_not_applicable(-1)

    with pytest.raises(TypeError):
        case_stat.set_not_applicable("not a number")