# -*- coding: utf-8 -*-
""" Confluence sender module """

from atlassian import Confluence

from ..engines.plotly_reporter import PlotlyReporter
from ..utils.logger_config import setup_logger, DEFAULT_LOGGING_LEVEL


class ConfluenceSender:
    """Class contains wrapper for generating and sends reports to Confluence"""

    def __init__(
        self,
        url=None,
        username=None,
        password=None,
        confluence_page=None,
        automation_platforms=None,
        type_platforms=None,
        plotly_engine=None,
        logger=None,
        log_level=DEFAULT_LOGGING_LEVEL,
    ):
        """
        General init

        :param url: url of Confluence, string, required
        :param username: username of Confluence user with proper access rights, string, required
        :param password: password of Confluence user with proper access rights, string, required
        :param confluence_page: confluence page short URL, string - only last part of it (it's id or str), optional
        :param automation_platforms: list of dicts of automation platforms, dict = {'name': 'Desktop Chrome',
                                                                                    'internal_name': 'type_id',
                                                                                    'sections': [16276]}, optional
        :param type_platforms: list of dicts, with sections ids, where dict = {'name': 'UI',
                                                                               'sections': [16276]}, optional
        :param plotly_engine: custom graphic reporter engine (PlotlyReporter), if none is selected, new will be created
        :param logger: logger object, optional
        :param log_level: logging level, optional, by default is 'logging.DEBUG'
        """
        if not logger:
            self.___logger = setup_logger(name="ConfluenceReporter", log_file="ConfluenceReporter.log", level=log_level)
        else:
            self.___logger = logger
        self.___logger.debug("ConfluenceReporter init")
        if url is None or username is None or password is None:
            raise ValueError("No confluence credentials are provided!")
        self.__confluence = Confluence(url=url, username=username, password=password)
        self.__confluence_page = confluence_page  # confluence page may vary for each report if needed, None is possible
        self.__plotly = (
            plotly_engine if plotly_engine else PlotlyReporter(type_platforms=type_platforms, log_level=log_level)
        )
        self.__automation_platforms = automation_platforms  # should be passed with specific TestRails sections
        self.__type_platforms = type_platforms

    def automation_state(self, confluence_page=None, reports=None, filename="current_automation.png"):
        """
        Generates and sends (attach) an image file (png) to confluence page with staked distribution (bar chart)
        with automation type coverage (or similar).

        :param confluence_page: confluence page short URL, string - only last part of it (it's id or str), optional
        :param reports: report with stacked distribution, usually it output of
                        ATCoverageReporter().automation_state_report()
        :param filename: filename of image (with a valid path), png expected
        :return: none
        """
        if not confluence_page:
            raise ValueError("No confluence page is provided, report aborted!")
        if not reports:
            raise ValueError("No TestRail reports are provided, report aborted!")
        self.__plotly.draw_automation_state_report(reports=reports, filename=filename)
        self.__confluence.attach_file(filename, page_id=confluence_page, title="current_automation")

    def test_case_priority_distribution(
        self, confluence_page=None, values=None, filename="current_priority_distribution.png"
    ):
        """
        Generates and sends (attach) an image file (png) to confluence page with priority distribution (pie chart)

        :param confluence_page: confluence page short URL, string - only last part of it (it's id or str), optional
        :param values: list of values to draw a report with priority distribution, usually it's output from
                       ATCoverageReporter().test_case_by_priority()
        :param filename: filename of image (maybe with a valid path), png expected
        :return: none
        """
        if not confluence_page:
            raise ValueError("No confluence page is provided, report aborted!")
        if not values:
            raise ValueError("No TestRail reports are provided, report aborted!")
        self.__plotly.draw_test_case_by_priority(values=values, filename=filename)
        self.__confluence.attach_file(filename, page_id=confluence_page, title="current_priority_distribution")

    def test_case_area_distribution(self, confluence_page=None, cases=None, filename="current_area_distribution.png"):
        """
        Generates and sends (attach) an image file (png) to confluence page with sections distribution (pie chart)

        :param confluence_page: confluence page short URL, string - only last part of it (it's id or str), optional
        :param cases: list of values to draw a report with priority distribution, usually it's output from
                       ATCoverageReporter().test_case_by_type()
        :param filename: filename of image (maybe with a valid path), png expected
        :return: none
        """
        if not confluence_page:
            raise ValueError("No confluence page is provided, report aborted!")
        if not cases:
            raise ValueError("No TestRail cases are provided, report aborted!")
        self.__plotly.draw_test_case_by_area(cases=cases, filename=filename)
        self.__confluence.attach_file(filename, page_id=confluence_page, title="current_area_distribution")

    def history_state_chart(self, confluence_page=None, automation_platforms=None):
        """
        Generates and sends (attach) an image file (png) to confluence page with state distribution (staked line chart)

        :param confluence_page: confluence page short URL, string - only last part of it (it's id or str), optional
        :param automation_platforms: list of dicts contains automation platforms = [{'name': 'Desktop Chrome',
                                                                                     'internal_name': 'type_id',
                                                                                     'sections': [16276]}]
        :return: none
        """
        automation_platforms = automation_platforms if automation_platforms else self.__automation_platforms
        if not confluence_page:
            raise ValueError("No confluence page is provided, report aborted!")
        if automation_platforms is None:
            raise ValueError("No automation platforms provided, report aborted!")
        for item in automation_platforms:
            self.___logger.debug("generating chart for %s", item["name"])
            filename = self.__plotly.draw_history_state_chart(chart_name=item["name"])
            self.__confluence.attach_file(filename, page_id=confluence_page, title=filename[:-4])

    def history_type_chart(
        self, confluence_page=None, type_platforms=None, filename="current_area_distribution_history.png"
    ):
        """
        Generates and sends (attach) an image file (png) to confluence page with state distribution (staked line chart)

        :param confluence_page: confluence page short URL, string - only last part of it (it's id or str), optional
        :param type_platforms: list of dicts, with sections ids, where dict = {'name': 'UI',
                                                                               'sections': [16276]}
        :param filename: filename of image (maybe with valid path), png expected
        :return: none
        """
        type_platforms = type_platforms if type_platforms else self.__type_platforms
        if not confluence_page:
            raise ValueError("No confluence page is provided, report aborted!")
        if not type_platforms:
            raise ValueError("No type platforms specified, report aborted!")
        self.__plotly.draw_history_type_chart(type_platforms=type_platforms, filename=filename)
        self.__confluence.attach_file(filename, page_id=confluence_page, title="current_area_distribution_history")

    def generate_report(
        self,
        confluence_page=None,
        reports=None,
        cases=None,
        values=None,
        type_platforms=None,
        automation_platforms=None,
    ):
        """
        Generates and sends (attach) an image file (png) to confluence page with state distribution (staked line chart)

        :param confluence_page: confluence page short URL, string - only last part of it (it's id or str), optional
        :param reports: report with stacked distribution, usually it's output of
                        ATCoverageReporter().automation_state_report()
        :param cases: list of values to draw report with priority distribution, usually it's output from
                      ATCoverageReporter().test_case_by_type()
        :param values: list of values to draw report with priority distribution, usually it's output from
                       ATCoverageReporter().test_case_by_priority()
        :param type_platforms: list of dicts, with sections ids, where dict = {'name': 'UI',
                                                                               'sections': [16276]}, optional
        :param automation_platforms: list of dicts of automation platforms, dict = {'name': 'Desktop Chrome',
                                                                                    'internal_name': 'type_id',
                                                                                    'sections': [16276]}, optional
        :return: none
        """
        confluence_page = confluence_page if confluence_page else self.__confluence_page
        if not confluence_page:
            raise ValueError("No confluence page is provided, report aborted!")
        if not reports:
            raise ValueError("No TestRail reports are provided, report aborted!")
        if not cases:
            raise ValueError("No TestRail cases are provided, report aborted!")
        if not values:
            raise ValueError("No TestRail values are provided, report aborted!")
        type_platforms = type_platforms if type_platforms else self.__type_platforms
        if not type_platforms:
            raise ValueError("No type platforms specified, report aborted!")
        automation_platforms = automation_platforms if automation_platforms else self.__automation_platforms
        if not automation_platforms:
            raise ValueError("No type platforms specified, report aborted!")
        self.automation_state(confluence_page=confluence_page, reports=reports)
        self.test_case_priority_distribution(confluence_page=confluence_page, values=values)
        self.test_case_area_distribution(confluence_page=confluence_page, cases=cases)
        self.history_type_chart(confluence_page=confluence_page)
        self.history_state_chart(confluence_page=confluence_page)
