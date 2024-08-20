"""Conftest for testsuite"""

from os import path, remove

import pytest
from faker import Faker


@pytest.fixture
def create_test_file():
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

