# -*- coding: utf-8 -*-
"""AI provider adapters used to generate test case content from automated tests"""

from abc import ABC, abstractmethod
from typing import Callable, Optional


class AIContentProvider(ABC):
    """Base class for an AI provider able to generate text from a prompt"""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text for the given prompt

        :param prompt: user prompt, string
        :param system_prompt: system/instructions prompt, string, optional
        :return: generated text, string
        """


class OpenAIProvider(AIContentProvider):
    """AI provider backed by OpenAI chat completions API"""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini", temperature: float = 0.2, **client_kwargs):
        """
        Init OpenAI provider

        :param api_key: OpenAI API key, string
        :param model: model name, string, by default "gpt-4o-mini"
        :param temperature: sampling temperature, float
        :param client_kwargs: extra kwargs passed to the OpenAI client
        """
        try:
            from openai import OpenAI  # pylint: disable=import-outside-toplevel
        except ImportError as error:
            raise ImportError(
                "OpenAIProvider requires the 'openai' package, install it via `pip install openai`"
            ) from error
        self.__client = OpenAI(api_key=api_key, **client_kwargs)
        self.__model = model
        self.__temperature = temperature

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text via OpenAI chat completions

        :param prompt: user prompt, string
        :param system_prompt: system/instructions prompt, string, optional
        :return: generated text, string
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = self.__client.chat.completions.create(
            model=self.__model, messages=messages, temperature=self.__temperature
        )
        return response.choices[0].message.content


class CohereProvider(AIContentProvider):
    """AI provider backed by Cohere chat API"""

    def __init__(self, api_key: str, model: str = "command-r-plus", temperature: float = 0.2, **client_kwargs):
        """
        Init Cohere provider

        :param api_key: Cohere API key, string
        :param model: model name, string, by default "command-r-plus"
        :param temperature: sampling temperature, float
        :param client_kwargs: extra kwargs passed to the Cohere client
        """
        try:
            import cohere  # pylint: disable=import-outside-toplevel
        except ImportError as error:
            raise ImportError(
                "CohereProvider requires the 'cohere' package, install it via `pip install cohere`"
            ) from error
        self.__client = cohere.Client(api_key, **client_kwargs)
        self.__model = model
        self.__temperature = temperature

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text via Cohere chat API

        :param prompt: user prompt, string
        :param system_prompt: system/instructions prompt, string, optional
        :return: generated text, string
        """
        response = self.__client.chat(
            message=prompt, preamble=system_prompt, model=self.__model, temperature=self.__temperature
        )
        return response.text


class AnthropicProvider(AIContentProvider):
    """AI provider backed by Anthropic messages API"""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-5-5",
        temperature: float = 0.2,
        max_tokens: int = 4096,
        **client_kwargs,
    ):
        """
        Init Anthropic provider

        :param api_key: Anthropic API key, string
        :param model: model name, string, by default "claude-sonnet-5-5"
        :param temperature: sampling temperature, float
        :param max_tokens: max tokens to generate, int
        :param client_kwargs: extra kwargs passed to the Anthropic client
        """
        try:
            from anthropic import Anthropic  # pylint: disable=import-outside-toplevel
        except ImportError as error:
            raise ImportError(
                "AnthropicProvider requires the 'anthropic' package, install it via `pip install anthropic`"
            ) from error
        self.__client = Anthropic(api_key=api_key, **client_kwargs)
        self.__model = model
        self.__temperature = temperature
        self.__max_tokens = max_tokens

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text via Anthropic messages API

        :param prompt: user prompt, string
        :param system_prompt: system/instructions prompt, string, optional
        :return: generated text, string
        """
        response = self.__client.messages.create(
            model=self.__model,
            max_tokens=self.__max_tokens,
            temperature=self.__temperature,
            system=system_prompt if system_prompt else "",
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if getattr(block, "type", None) == "text")


class CustomProvider(AIContentProvider):
    """AI provider that wraps an arbitrary user-supplied callable, to plug in any provider"""

    def __init__(self, generate_func: Callable[[str, Optional[str]], str]):
        """
        Init custom provider

        :param generate_func: callable accepting (prompt, system_prompt) and returning generated text, string
        """
        self.__generate_func = generate_func

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text via the wrapped callable

        :param prompt: user prompt, string
        :param system_prompt: system/instructions prompt, string, optional
        :return: generated text, string
        """
        return self.__generate_func(prompt, system_prompt)
