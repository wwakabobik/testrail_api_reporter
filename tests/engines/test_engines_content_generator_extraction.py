# -*- coding: utf-8 -*-
"""Tests for content_generator module, extraction and prompt helpers"""

from unittest.mock import MagicMock, patch

import pytest
from faker import Faker

from testrail_api_reporter.engines.content_generator import (  # pylint: disable=import-error,no-name-in-module
    TestCaseContentGenerator,
)

fake = Faker()


@pytest.fixture
def generator():
    """Fixture to return TestCaseContentGenerator with a mocked TestRailAPI and a mocked AI provider"""
    with patch("testrail_api_reporter.engines.content_generator.TestRailAPI"):
        return TestCaseContentGenerator(
            url=fake.url(),
            email=fake.email(),
            password=fake.password(),
            project_id=fake.random_int(),
            provider=MagicMock(),
        )


@pytest.fixture
def test_file(tmp_path):
    """Fixture to return a path to a python file with a standalone test and a class-based test"""
    content = '''
def not_a_test():
    """Should be ignored, does not start with 'test'"""
    return 1


def test_standalone():
    """A standalone test"""
    assert 1 + 1 == 2


class TestSomething:
    def test_in_class(self):
        """A test inside a class"""
        assert True

    def helper(self):
        """Should be ignored, does not start with 'test'"""
        return None
'''
    file_path = tmp_path / "test_sample.py"
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)


def test_extract_tests_from_file(generator, test_file):  # pylint: disable=redefined-outer-name
    """extract_tests_from_file should find both standalone and class-based tests, skipping non-test functions"""
    tests = generator.extract_tests_from_file(test_file)

    names = {test["name"] for test in tests}
    assert names == {"test_standalone", "test_in_class"}

    standalone = next(test for test in tests if test["name"] == "test_standalone")
    assert standalone["automation_id"].endswith("test_sample.test_standalone")
    assert standalone["docstring"] == "A standalone test"
    assert "assert 1 + 1 == 2" in standalone["source"]

    in_class = next(test for test in tests if test["name"] == "test_in_class")
    assert in_class["automation_id"].endswith("test_sample.TestSomething.test_in_class")
    assert in_class["docstring"] == "A test inside a class"


def test_build_prompt_includes_docstring_source_and_context(
    generator, test_file
):  # pylint: disable=redefined-outer-name
    """__build_prompt should include the test name, docstring, source and extra context when provided"""
    test = generator.extract_tests_from_file(test_file)[0]
    extra_context = fake.sentence()

    # pylint: disable=protected-access,no-member
    prompt = generator._TestCaseContentGenerator__build_prompt(test, extra_context=extra_context)

    assert test["name"] in prompt
    assert test["docstring"] in prompt
    assert test["source"] in prompt
    assert extra_context in prompt


def test_build_prompt_without_docstring_or_context(generator, test_file):  # pylint: disable=redefined-outer-name
    """__build_prompt should omit the docstring section when there is no docstring, and work without extra context"""
    test = dict(generator.extract_tests_from_file(test_file)[0])
    test["docstring"] = None

    # pylint: disable=protected-access,no-member
    prompt = generator._TestCaseContentGenerator__build_prompt(test)

    assert "Docstring:" not in prompt
