# -*- coding: utf-8 -*-
"""Tests for the ai_providers module"""

import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import MagicMock

import pytest
from faker import Faker

from testrail_api_reporter.utils.ai_providers import (  # pylint: disable=import-error,no-name-in-module
    AIContentProvider,
    AnthropicProvider,
    CohereProvider,
    CustomProvider,
    OpenAIProvider,
)

fake = Faker()


def test_ai_content_provider_is_abstract():
    """AIContentProvider cannot be instantiated directly"""
    with pytest.raises(TypeError):
        AIContentProvider()  # pylint: disable=abstract-class-instantiated


def test_custom_provider_generate():
    """CustomProvider forwards prompt/system_prompt to the wrapped callable"""
    prompt = fake.sentence()
    system_prompt = fake.sentence()
    expected = fake.sentence()
    generate_func = MagicMock(return_value=expected)

    provider = CustomProvider(generate_func=generate_func)
    result = provider.generate(prompt=prompt, system_prompt=system_prompt)

    generate_func.assert_called_once_with(prompt, system_prompt)
    assert result == expected


def test_openai_provider_missing_dependency(monkeypatch):
    """OpenAIProvider raises a clear ImportError if 'openai' package is missing"""
    monkeypatch.setitem(sys.modules, "openai", None)
    with pytest.raises(ImportError, match="openai"):
        OpenAIProvider(api_key=fake.password())


def test_openai_provider_generate(monkeypatch):
    """OpenAIProvider.generate calls the OpenAI chat completions API and returns its content"""
    expected = fake.sentence()
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=expected))]
    )
    fake_module = ModuleType("openai")
    fake_module.OpenAI = MagicMock(return_value=mock_client)
    monkeypatch.setitem(sys.modules, "openai", fake_module)

    api_key = fake.password()
    provider = OpenAIProvider(api_key=api_key, model="gpt-4o-mini")
    prompt = fake.sentence()
    system_prompt = fake.sentence()
    result = provider.generate(prompt=prompt, system_prompt=system_prompt)

    fake_module.OpenAI.assert_called_once_with(api_key=api_key)
    mock_client.chat.completions.create.assert_called_once_with(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
        temperature=0.2,
    )
    assert result == expected


def test_openai_provider_generate_without_system_prompt(monkeypatch):
    """OpenAIProvider.generate omits the system message when no system_prompt is provided"""
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=fake.sentence()))]
    )
    fake_module = ModuleType("openai")
    fake_module.OpenAI = MagicMock(return_value=mock_client)
    monkeypatch.setitem(sys.modules, "openai", fake_module)

    provider = OpenAIProvider(api_key=fake.password())
    prompt = fake.sentence()
    provider.generate(prompt=prompt)

    _, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs["messages"] == [{"role": "user", "content": prompt}]


def test_cohere_provider_missing_dependency(monkeypatch):
    """CohereProvider raises a clear ImportError if 'cohere' package is missing"""
    monkeypatch.setitem(sys.modules, "cohere", None)
    with pytest.raises(ImportError, match="cohere"):
        CohereProvider(api_key=fake.password())


def test_cohere_provider_generate(monkeypatch):
    """CohereProvider.generate calls the Cohere chat API and returns its text"""
    expected = fake.sentence()
    mock_client = MagicMock()
    mock_client.chat.return_value = SimpleNamespace(text=expected)
    fake_module = ModuleType("cohere")
    fake_module.Client = MagicMock(return_value=mock_client)
    monkeypatch.setitem(sys.modules, "cohere", fake_module)

    api_key = fake.password()
    provider = CohereProvider(api_key=api_key, model="command-r-plus")
    prompt = fake.sentence()
    system_prompt = fake.sentence()
    result = provider.generate(prompt=prompt, system_prompt=system_prompt)

    fake_module.Client.assert_called_once_with(api_key)
    mock_client.chat.assert_called_once_with(
        message=prompt, preamble=system_prompt, model="command-r-plus", temperature=0.2
    )
    assert result == expected


def test_anthropic_provider_missing_dependency(monkeypatch):
    """AnthropicProvider raises a clear ImportError if 'anthropic' package is missing"""
    monkeypatch.setitem(sys.modules, "anthropic", None)
    with pytest.raises(ImportError, match="anthropic"):
        AnthropicProvider(api_key=fake.password())


def test_anthropic_provider_generate(monkeypatch):
    """AnthropicProvider.generate calls the Anthropic messages API and concatenates text blocks"""
    part_one = fake.word()
    part_two = fake.word()
    mock_client = MagicMock()
    mock_client.messages.create.return_value = SimpleNamespace(
        content=[
            SimpleNamespace(type="text", text=part_one),
            SimpleNamespace(type="text", text=part_two),
            SimpleNamespace(type="other", text="ignored"),
        ]
    )
    fake_module = ModuleType("anthropic")
    fake_module.Anthropic = MagicMock(return_value=mock_client)
    monkeypatch.setitem(sys.modules, "anthropic", fake_module)

    api_key = fake.password()
    provider = AnthropicProvider(api_key=api_key, model="claude-sonnet-5-5")
    prompt = fake.sentence()
    system_prompt = fake.sentence()
    result = provider.generate(prompt=prompt, system_prompt=system_prompt)

    fake_module.Anthropic.assert_called_once_with(api_key=api_key)
    mock_client.messages.create.assert_called_once_with(
        model="claude-sonnet-5-5",
        max_tokens=4096,
        temperature=0.2,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}],
    )
    assert result == part_one + part_two
