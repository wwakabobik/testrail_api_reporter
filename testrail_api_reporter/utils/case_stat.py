""" CaseStat class """


class CaseStat:
    """
    Placeholder class for automation statistics
    """

    def __init__(self, name):
        """
        Constructor

        :param name: name of the test case
        """
        self.name = name
        self.total = 0
        self.automated = 0
        self.not_automated = 0
        self.not_applicable = 0

    # getters
    def get_name(self):
        """
        Returns the name of the test case

        :return: name of the test case
        """
        return self.name

    def get_total(self):
        """
        Returns the total number of test cases

        :return: total number of test cases
        """
        return self.total

    def get_automated(self):
        """
        Returns the number of automated test cases

        :return: number of automated test cases
        """
        return self.automated

    def get_not_automated(self):
        """
        Returns the number of not automated test cases

        :return: number of not automated test cases
        """
        return self.not_automated

    def get_not_applicable(self):
        """
        Returns the number of not applicable test cases

        :return: number of not applicable test cases
        """
        return self.not_applicable

    # setters
    def set_name(self, name):
        """
        Sets the name of the test case

        :param name: name of the test case
        """
        self.name = name

    def set_total(self, total):
        """
        Sets the total number of test cases

        :param total: total number of test cases
        """
        self.total = total

    def set_automated(self, automated):
        """
        Sets the number of automated test cases

        :param automated: number of automated test cases
        """
        self.automated = automated

    def set_not_automated(self, not_automated):
        """
        Sets the number of not automated test cases

        :param not_automated: number of not automated test cases
        """
        self.not_automated = not_automated

    def set_not_applicable(self, not_applicable):
        """
        Sets the number of not applicable test cases

        :param not_applicable: number of not applicable test cases
        """
        self.not_applicable = not_applicable
