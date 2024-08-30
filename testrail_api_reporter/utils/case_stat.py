# -*- coding: utf-8 -*-
""" CaseStat class """


class CaseStat:
    """Placeholder class for automation statistics"""

    def __init__(self, name: str):
        """
        Constructor

        :param name: name of the test case
        """
        self.name: str = name
        self.total: int = 0
        self.automated: int = 0
        self.not_automated: int = 0
        self.not_applicable: int = 0

    # getters
    def get_name(self) -> str:
        """
        Returns the name of the test case

        :return: name of the test case
        """
        return self.name

    def get_total(self) -> int:
        """
        Returns the total number of test cases

        :return: total number of test cases
        """
        return self.total

    def get_automated(self) -> int:
        """
        Returns the number of automated test cases

        :return: number of automated test cases
        """
        return self.automated

    def get_not_automated(self) -> int:
        """
        Returns the number of not automated test cases

        :return: number of not automated test cases
        """
        return self.not_automated

    def get_not_applicable(self) -> int:
        """
        Returns the number of not applicable test cases

        :return: number of not applicable test cases
        """
        return self.not_applicable

    # setters
    def set_name(self, name: str) -> None:
        """
        Sets the name of the test case

        :param name: name of the test case
        """
        self.name = name

    def set_total(self, total: int) -> None:
        """
        Sets the total number of test cases

        :param total: total number of test cases
        """
        if total < 0:
            raise ValueError("State value 'total' can't be less than 0")
        self.total = total

    def set_automated(self, automated: int):
        """
        Sets the number of automated test cases

        :param automated: number of automated test cases
        """
        if automated < 0:
            raise ValueError("State value 'automated' can't be less than 0")
        self.automated = automated

    def set_not_automated(self, not_automated: int) -> None:
        """
        Sets the number of not automated test cases

        :param not_automated: number of not automated test cases
        """
        if not_automated < 0:
            raise ValueError("State value 'not_automated' can't be less than 0")
        self.not_automated = not_automated

    def set_not_applicable(self, not_applicable):
        """
        Sets the number of not applicable test cases

        :param not_applicable: number of not applicable test cases
        """
        if not_applicable < 0:
            raise ValueError("State value 'not_applicable' can't be less than 0")
        self.not_applicable = not_applicable
