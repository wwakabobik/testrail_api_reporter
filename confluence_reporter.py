from plotly_reporter import PlotlyReporter
from atlassian import Confluence


class ConfluenceReporter:
    def __init__(self, url, username, password, confluence_page=None, automation_platforms=None, plotly_engine=None,
                 debug=True):
        if debug:
            print("\nConfluence Reporter init")
        if url is None or username is None or password is None:
            raise Exception("No confluence credentials are provided!")
        else:
            self.__confluence = Confluence(url=url, username=username, password=password)
        self.__confluence_page = confluence_page  # confluence page may vary for each report if needed, None is possible
        self.__debug = debug
        self.__plotly = plotly_engine if plotly_engine else PlotlyReporter(debug=debug)
        self.__automation_platforms = automation_platforms  # should be passed with specific TestRails sections

    def automation_state(self, confluence_page=None, reports=None, filename='current_automation.png', debug=None):
        if not confluence_page:
            raise Exception("No confluence page is provided, report aborted!")
        if not reports:
            raise Exception("No TestRail reports are provided, report aborted!")
        debug = debug if debug is not None else self.__debug
        self.__plotly.draw_automation_state_report(reports=reports, filename=filename, debug=debug)
        self.__confluence.attach_file(filename, page_id=confluence_page, title='current_automation')

    def test_case_priority_distribution(self, confluence_page=None, values=None,
                                        filename='current_priority_distribution.png', debug=None):
        if not confluence_page:
            raise Exception("No confluence page is provided, report aborted!")
        if not values:
            raise Exception("No TestRail reports are provided, report aborted!")
        debug = debug if debug is not None else self.__debug
        self.__plotly.draw_test_case_by_priority(values=values, filename=filename, debug=debug)
        self.__confluence.attach_file(filename, page_id=confluence_page, title='current_priority_distribution')

    def test_case_area_distribution(self, confluence_page=None, cases=None, filename='current_area_distribution.png',
                                    debug=None):
        if not confluence_page:
            raise Exception("No confluence page is provided, report aborted!")
        if not cases:
            raise Exception("No TestRail cases are provided, report aborted!")
        debug = debug if debug is not None else self.__debug
        self.__plotly.draw_test_case_by_area(cases=cases, filename=filename, debug=debug)
        self.__confluence.attach_file(filename, page_id=confluence_page, title='current_area_distribution')

    def history_state_chart(self, confluence_page, automation_platforms=None, debug=None):
        automation_platforms = automation_platforms if automation_platforms else self.__automation_platforms
        debug = debug if debug is not None else self.__debug
        if not confluence_page:
            raise Exception("No confluence page is provided, report aborted!")
        if automation_platforms is None:
            raise Exception("No automation platforms provided, report aborted!")
        for item in automation_platforms:
            if debug:
                print(f"generating chart for {item['name']}")
            filename = self.__plotly.draw_history_state_chart(debug=debug, chart_name=item['name'])
            self.__confluence.attach_file(filename, page_id=confluence_page, title=filename[:-4])

    def history_type_chart(self, confluence_page, filename='current_area_distribution_history.png', debug=None):
        debug = debug if debug is not None else self.__debug
        if not confluence_page:
            raise Exception("No confluence page is provided, report aborted!")
        self.__plotly.draw_history_type_chart(debug=debug, filename=filename)
        self.__confluence.attach_file(filename, page_id=confluence_page, title='current_area_distribution_history')

    def generate_report(self, confluence_page, debug=None):
        debug = debug if debug is not None else self.__debug
        if not confluence_page:
            raise Exception("No confluence page is provided, report aborted!")
        self.automation_state(debug=debug, confluence_page=confluence_page)
        self.test_case_priority_distribution(debug=debug, confluence_page=confluence_page)
        self.test_case_area_distribution(debug=debug, confluence_page=confluence_page)
        self.history_type_chart(debug=debug, confluence_page=confluence_page)
        self.history_state_chart(debug=debug, confluence_page=confluence_page)
