from atlassian import Confluence
from plotly_reporter import PlotlyReporter


class ConfluenceReporter:
    def __init__(self, url=None, username=None, password=None, confluence_page=None, automation_platforms=None,
                 plotly_engine=None, type_platforms=None, debug=True):
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

    def automation_state(self, confluence_page=None, reports=None, filename='current_automation.png', debug=None):
        if not confluence_page:
            raise ValueError("No confluence page is provided, report aborted!")
        if not reports:
            raise ValueError("No TestRail reports are provided, report aborted!")
        debug = debug if debug is not None else self.__debug
        self.__plotly.draw_automation_state_report(reports=reports, filename=filename, debug=debug)
        self.__confluence.attach_file(filename, page_id=confluence_page, title='current_automation')

    def test_case_priority_distribution(self, confluence_page=None, values=None,
                                        filename='current_priority_distribution.png', debug=None):
        if not confluence_page:
            raise ValueError("No confluence page is provided, report aborted!")
        if not values:
            raise ValueError("No TestRail reports are provided, report aborted!")
        debug = debug if debug is not None else self.__debug
        self.__plotly.draw_test_case_by_priority(values=values, filename=filename, debug=debug)
        self.__confluence.attach_file(filename, page_id=confluence_page, title='current_priority_distribution')

    def test_case_area_distribution(self, confluence_page=None, cases=None, filename='current_area_distribution.png',
                                    debug=None):
        if not confluence_page:
            raise ValueError("No confluence page is provided, report aborted!")
        if not cases:
            raise ValueError("No TestRail cases are provided, report aborted!")
        debug = debug if debug is not None else self.__debug
        self.__plotly.draw_test_case_by_area(cases=cases, filename=filename, debug=debug)
        self.__confluence.attach_file(filename, page_id=confluence_page, title='current_area_distribution')

    def history_state_chart(self, confluence_page=None, automation_platforms=None, debug=None):
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

    def history_type_chart(self, confluence_page, filename='current_area_distribution_history.png', debug=None):
        debug = debug if debug is not None else self.__debug
        if not confluence_page:
            raise ValueError("No confluence page is provided, report aborted!")
        self.__plotly.draw_history_type_chart(debug=debug, filename=filename)
        self.__confluence.attach_file(filename, page_id=confluence_page, title='current_area_distribution_history')

    def generate_report(self, confluence_page, reports=None, cases=None, values=None, debug=None):
        if not confluence_page:
            raise ValueError("No confluence page is provided, report aborted!")
        if not reports:
            raise ValueError("No TestRail reports are provided, report aborted!")
        if not cases:
            raise ValueError("No TestRail cases are provided, report aborted!")
        if not values:
            raise ValueError("No TestRail values are provided, report aborted!")
        debug = debug if debug is not None else self.__debug
        self.automation_state(confluence_page=confluence_page, reports=reports, debug=debug)
        self.test_case_priority_distribution(confluence_page=confluence_page, values=values, debug=debug)
        self.test_case_area_distribution(confluence_page=confluence_page, cases=cases, debug=debug)
        self.history_type_chart(confluence_page=confluence_page, debug=debug)
        self.history_state_chart(confluence_page=confluence_page, debug=debug)
