# -*- coding: utf-8 -*-
"""Tests for the case_stat module, сlass 'CaseStat'"""

import pytest
from faker import Faker

from testrail_api_reporter.utils.case_stat import CaseStat  # pylint: disable=import-error,no-name-in-module

fake = Faker()


def test_case_stat_init():
    """Check default CaseStat init"""
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


def test_case_stat_total(case_stat):
    """Check total"""
    total = fake.random_number()
    case_stat.set_total(total)
    assert case_stat.get_total() == total, "Total number of test cases does not match"


def test_case_stat_automated(case_stat):
    """Check automated"""
    automated = fake.random_number()
    case_stat.set_automated(automated)
    assert case_stat.get_automated() == automated, "Number of automated test cases does not match"


def test_case_stat_not_automated(case_stat):
    """Check not automated"""
    not_automated = fake.random_number()
    case_stat.set_not_automated(not_automated)
    assert case_stat.get_not_automated() == not_automated, "Number of not automated test cases does not match"


def test_case_stat_not_applicable(case_stat):
    """Check not applicable"""
    not_applicable = fake.random_number()
    case_stat.set_not_applicable(not_applicable)
    assert case_stat.get_not_applicable() == not_applicable, "Number of not applicable test cases does not match"


def test_case_stat_negative_total(case_stat):
    """Negative case for total"""
    with pytest.raises(ValueError):
        case_stat.set_total(-1)


def test_case_stat_total_not_a_number(case_stat):
    """Negative case for total - incorrect type"""
    with pytest.raises(TypeError):
        case_stat.set_total("not a number")  # type: ignore


def test_case_stat_negative_automated(case_stat):
    """Negative case for automated"""
    with pytest.raises(ValueError):
        case_stat.set_automated(-1)


def test_case_stat_automated_not_a_number(case_stat):
    """Negative case for automated - incorrect type"""
    with pytest.raises(TypeError):
        case_stat.set_automated("not a number")  # type: ignore


def test_case_stat_negative_not_automated(case_stat):
    """Negative case for not_automated"""
    with pytest.raises(ValueError):
        case_stat.set_not_automated(-1)


def test_case_stat_not_automated_not_a_number(case_stat):
    """Negative case for not automated - incorrect type"""
    with pytest.raises(TypeError):
        case_stat.set_not_automated("not a number")  # type: ignore


def test_case_stat_negative_not_applicable(case_stat):
    """Negative case for not applicable"""
    with pytest.raises(ValueError):
        case_stat.set_not_applicable(-1)


def test_case_stat_not_applicable_not_a_number(case_stat):
    """Negative case for not applicable - incorrect type"""
    with pytest.raises(TypeError):
        case_stat.set_not_applicable("not a number")
