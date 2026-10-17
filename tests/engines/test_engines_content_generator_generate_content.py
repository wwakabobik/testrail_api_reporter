# -*- coding: utf-8 -*-
"""Tests for content_generator module, the generate_content/generate_for_file methods"""

import json
from unittest.mock import MagicMock, patch

import pytest
from faker import Faker

from testrail_api_reporter.engines.content_generator import (  # pylint: disable=import-error,no-name-in-module
    TestCaseContentGenerator,
)

fake = Faker()


def _sample_content():
    """Build a sample generated-content dict"""
    return {
        "title": fake.sentence(),
        "preconditions": fake.sentence(),
        "steps": fake.sentence(),
        "expected_result": fake.sentence(),
        "description": fake.sentence(),
    }


@pytest.fixture
def provider():
    """Fixture to return a mocked AI provider"""
    return MagicMock()


@pytest.fixture
def generator(provider):  # pylint: disable=redefined-outer-name
    """Fixture to return TestCaseContentGenerator with a mocked TestRailAPI and the mocked AI provider"""
    with patch("testrail_api_reporter.engines.content_generator.TestRailAPI"):
        return TestCaseContentGenerator(
            url=fake.url(),
            email=fake.email(),
            password=fake.password(),
            project_id=fake.random_int(),
            provider=provider,
        )


@pytest.fixture
def test_dict():
    """Fixture to return a minimal extracted-test dict"""
    return {"automation_id": "pkg.mod.test_example", "name": "test_example", "docstring": "doc", "source": "code"}


def test_generate_content_parses_plain_json(generator, provider, test_dict):  # pylint: disable=redefined-outer-name
    """generate_content should parse a plain JSON response from the provider"""
    content = _sample_content()
    provider.generate.return_value = json.dumps(content)

    result = generator.generate_content(test_dict)

    assert result == content


def test_generate_content_strips_markdown_fences(
    generator, provider, test_dict
):  # pylint: disable=redefined-outer-name
    """generate_content should tolerate a response wrapped in ```json ... ``` fences"""
    content = _sample_content()
    provider.generate.return_value = f"```json\n{json.dumps(content)}\n```"

    result = generator.generate_content(test_dict)

    assert result == content


def test_generate_content_passes_system_prompt_and_prompt(
    generator, provider, test_dict
):  # pylint: disable=redefined-outer-name
    """generate_content should call the provider with the built prompt and configured system prompt"""
    provider.generate.return_value = json.dumps(_sample_content())

    generator.generate_content(test_dict, extra_context="extra")

    _, kwargs = provider.generate.call_args
    assert test_dict["name"] in kwargs["prompt"]
    assert "extra" in kwargs["prompt"]
    # pylint: disable=protected-access,no-member
    assert kwargs["system_prompt"] == generator._TestCaseContentGenerator__system_prompt


def test_generate_content_invalid_json_returns_empty_dict(
    generator, provider, test_dict
):  # pylint: disable=redefined-outer-name
    """generate_content should log and return {} when the provider's response is not valid JSON"""
    provider.generate.return_value = "not json at all"

    result = generator.generate_content(test_dict)

    assert result == {}


def test_generate_for_file(generator, provider, tmp_path):  # pylint: disable=redefined-outer-name
    """generate_for_file should extract tests from a file and generate content for each of them"""
    file_path = tmp_path / "test_sample.py"
    file_path.write_text(
        'def test_one():\n    """doc"""\n    assert True\n\n\ndef test_two():\n    assert True\n', encoding="utf-8"
    )
    contents = [_sample_content(), _sample_content()]
    provider.generate.side_effect = [json.dumps(content) for content in contents]

    results = generator.generate_for_file(str(file_path))

    assert len(results) == 2
    assert {r["automation_id"] for r in results} == {
        f"{generator._TestCaseContentGenerator__automation_id(str(file_path), 'test_one')}",  # pylint: disable=protected-access,no-member
        f"{generator._TestCaseContentGenerator__automation_id(str(file_path), 'test_two')}",  # pylint: disable=protected-access,no-member
    }
    assert [r["content"] for r in results] == contents
