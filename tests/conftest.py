# -*- coding: utf-8 -*-
"""Conftest for testsuite"""

from os import path, remove
from random import randint

import pytest
from faker import Faker
from PIL import Image, ImageChops

from testrail_api_reporter.engines.plotly_reporter import (  # pylint: disable=import-error,no-name-in-module
    PlotlyReporter,
)
from testrail_api_reporter.utils.case_stat import CaseStat  # pylint: disable=import-error,no-name-in-module


fake = Faker()


@pytest.fixture
def create_test_file():
    """
    Fixture to create random test file

    :return: filename
    :rtype: str (generator)
    """
    test_file = f"not_existing_{fake.file_name()}"
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
def random_stat() -> tuple:
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
    return CaseStat(fake.word())


@pytest.fixture
def case_stat_random(case_stat, random_stat):  # pylint: disable=redefined-outer-name
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
def csv_file():
    """
    Fixture to create random test file

    :return: filename
    :rtype: str (generator)
    """
    test_file = f"not_existing_{fake.file_name(extension='csv')}"
    with open(test_file, "w", encoding="utf-8") as file:
        file.write("")
    assert path.exists(test_file) is True
    yield test_file
    # Cleanup if not removed by tests
    try:
        remove(test_file)
    except FileNotFoundError:
        pass


@pytest.fixture
def compare_image():
    """
    Fixture to compare images using pixel threshold

    :return: comparison function
    :rtype: function
    """

    def compare(actual: str, expected: str, threshold: int = 10) -> bool:
        """
        Function to compare images using pixel threshold

        :param actual: filename with path to actual image
        :type actual: str
        :param expected: filename with path to expected image
        :type actual: str
        :param threshold: pixel difference tolerance between images - lesser is better
        :type actual: int
        :return: comparison result. True if images match.
        :rtype: bool
        """
        # Ensure that images exists
        assert path.exists(actual)
        assert path.exists(expected)

        # Load the generated image and the reference image
        generated_image = Image.open(actual)
        reference_image = Image.open(expected)

        # Compare the two images
        diff = ImageChops.difference(generated_image, reference_image)

        # Count the number of pixels that are different
        diff_pixels = sum(abs(r - g) + abs(g - b) + abs(b - a) + abs(a - r) > 20 for r, g, b, a in diff.getdata())

        # Check that the number of different pixels is below the threshold
        return diff_pixels < threshold

    return compare


@pytest.fixture
def random_type_platforms() -> list:
    """
    Returns random list with type platforms dict

    :return: list with type platforms dict
    :rtype: list[dict]
    """
    return [{"name": fake.word(), "sections": [randint(1, 10000)]} for _ in range(randint(1, 5))]


@pytest.fixture
def random_plotly_reporter(random_type_platforms) -> PlotlyReporter:  # pylint: disable=redefined-outer-name
    """
    Returns PlotlyReporter object with random type platforms

    :return: PlotlyReporter object with random type platforms
    :rtype: PlotlyReporter
    """
    return PlotlyReporter(type_platforms=random_type_platforms)


@pytest.fixture()
def random_rgb():
    """Returns fixture to get rgb in string format"""

    def get_rgb() -> str:
        """
        Returns rgb in string format

        :return: rgb in string format
        :rtype: str
        """
        return f"rgb({randint(0, 255)},{randint(0, 255)},{randint(0, 255)})"

    return get_rgb
