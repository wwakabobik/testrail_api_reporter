from atlassian import Confluence

from .plotly_reporter import PlotlyReporter


class ConfluenceReporter:
    """
    Class contains wrapper for generate and send reports to Confluence
    """
    def __init__(self, url=None, username=None, password=None, confluence_page=None, automation_platforms=None,
                 type_platforms=None, plotly_engine=None, debug=True):
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
        :param debug: debug output is enabled, may be True or False, optional
        """
        if debug:
            print("\nConfluence Reporter init")
        if url is None or username is None or password is None:
            raise ValueError("No confluence credentials are provided!")
        else:
            self.__confluence = Confluence(url=url, username=username, password=password)
        self.__confluence_page = confluence_page  # confluence page may vary for each report if needed, None is possible
        self.__debug = debug
        self.__plotly = plotly_engine if plotly_engine else PlotlyReporter(type_platforms=type_platforms, debug=debug)
        self.__automation_platforms = automation_platforms  # should be passed with specific TestRails sections
        self.__type_platforms = type_platforms

    def automation_state(self, confluence_page=None, reports=None, filename='current_automation.png', debug=None):
        """
        Generates and sends (attach) an image file (png) to confluence page with staked distribution (bar chart)
        with automation type coverage (or similar).

        :param confluence_page: confluence page short URL, string - only last part of it (it's id or str), optional
        :param reports: report with stacked distribution, usually it's output of
                        ATCoverageReporter().automation_state_report()
        :param filename: filename of image (may be with valid path), png expected
        :param debug: debug output is enabled, may be True or False, optional
        :return: none
        """
        if not confluence_page:
            raise ValueError("No confluence page is provided, report aborted!")
        if not reports:
            raise ValueError("No TestRail reports are provided, report aborted!")
        debug = debug if debug is not None else self.__debug
        self.__plotly.draw_automation_state_report(reports=reports, filename=filename, debug=debug)
        self.__confluence.attach_file(filename, page_id=confluence_page, title='current_automation')

    def test_case_priority_distribution(self, confluence_page=None, values=None,
                                        filename='current_priority_distribution.png', debug=None):
        """
        Generates and sends (attach) an image file (png) to confluence page with priority distribution (pie chart)

        :param confluence_page: confluence page short URL, string - only last part of it (it's id or str), optional
        :param values: list of values to draw report with priority distribution, usually it's output from
                       ATCoverageReporter().test_case_by_priority()
        :param filename: filename of image (maybe with valid path), png expected
        :param debug: debug output is enabled, may be True or False, optional
        :return: none
        """
        if not confluence_page:
            raise ValueError("No confluence page is provided, report aborted!")
        if not values:
            raise ValueError("No TestRail reports are provided, report aborted!")
        debug = debug if debug is not None else self.__debug
        self.__plotly.draw_test_case_by_priority(values=values, filename=filename, debug=debug)
        self.__confluence.attach_file(filename, page_id=confluence_page, title='current_priority_distribution')

    def test_case_area_distribution(self, confluence_page=None, cases=None, filename='current_area_distribution.png',
                                    debug=None):
        """
        Generates and sends (attach) an image file (png) to confluence page with sections distribution (pie chart)

        :param confluence_page: confluence page short URL, string - only last part of it (it's id or str), optional
        :param cases: list of values to draw report with priority distribution, usually it's output from
                       ATCoverageReporter().test_case_by_type()
        :param filename: filename of image (maybe with valid path), png expected
        :param debug: debug output is enabled, may be True or False, optional
        :return: none
        """
        if not confluence_page:
            raise ValueError("No confluence page is provided, report aborted!")
        if not cases:
            raise ValueError("No TestRail cases are provided, report aborted!")
        debug = debug if debug is not None else self.__debug
        self.__plotly.draw_test_case_by_area(cases=cases, filename=filename, debug=debug)
        self.__confluence.attach_file(filename, page_id=confluence_page, title='current_area_distribution')

    def history_state_chart(self, confluence_page=None, automation_platforms=None, debug=None):
        """
        Generates and sends (attach) an image file (png) to confluence page with state distribution (staked line chart)

        :param confluence_page: confluence page short URL, string - only last part of it (it's id or str), optional
        :param automation_platforms: list of dicts of automation platforms, dict = {'name': 'Desktop Chrome',
                                                                                    'internal_name': 'type_id',
                                                                                    'sections': [16276]}
        :param debug: debug output is enabled, may be True or False, optional
        :return: none
        """
        automation_platforms = automation_platforms if automation_platforms else self.__automation_platforms
        debug = debug if debug is not None else self.__debug
        if not confluence_page:
            raise ValueError("No confluence page is provided, report aborted!")
        if automation_platforms is None:
            raise ValueError("No automation platforms provided, report aborted!")
        for item in automation_platforms:
            if debug:
                print(f"generating chart for {item['name']}")
            filename = self.__plotly.draw_history_state_chart(debug=debug, chart_name=item['name'])
            self.__confluence.attach_file(filename, page_id=confluence_page, title=filename[:-4])

    def history_type_chart(self, confluence_page=None, type_platforms=None,
                           filename='current_area_distribution_history.png', debug=None):
        """
        Generates and sends (attach) an image file (png) to confluence page with state distribution (staked line chart)

        :param confluence_page: confluence page short URL, string - only last part of it (it's id or str), optional
        :param type_platforms: list of dicts, with sections ids, where dict = {'name': 'UI',
                                                                               'sections': [16276]}
        :param filename: filename of image (maybe with valid path), png expected
        :param debug: debug output is enabled, may be True or False, optional
        :return: none
        """
        type_platforms = type_platforms if type_platforms else self.__type_platforms
        debug = debug if debug is not None else self.__debug
        if not confluence_page:
            raise ValueError("No confluence page is provided, report aborted!")
        if not type_platforms:
            raise ValueError("No type platforms specified, report aborted!")
        self.__plotly.draw_history_type_chart(debug=debug, type_platforms=type_platforms, filename=filename)
        self.__confluence.attach_file(filename, page_id=confluence_page, title='current_area_distribution_history')

    def generate_report(self, confluence_page=None, reports=None, cases=None, values=None, type_platforms=None,
                        automation_platforms=None, debug=None):
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
        debug = debug if debug is not None else self.__debug
        self.automation_state(confluence_page=confluence_page, reports=reports, debug=debug)
        self.test_case_priority_distribution(confluence_page=confluence_page, values=values, debug=debug)
        self.test_case_area_distribution(confluence_page=confluence_page, cases=cases, debug=debug)
        self.history_type_chart(confluence_page=confluence_page, debug=debug)
        self.history_state_chart(confluence_page=confluence_page, debug=debug)
