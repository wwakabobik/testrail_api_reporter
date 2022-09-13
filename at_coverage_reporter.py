from testrail_api import TestRailAPI

from .csv_parser import CSVParser
from .case_stat import CaseStat
from .reporter_utils import format_error


class ATCoverageReporter:
    """
    Class for generate data for automation coverage reports (or similar data) from TestRails
    """
    def __init__(self, url: str, email: str, password: str, priority=None, project=None, type_platforms=None,
                 automation_platforms=None, suite_id=None, debug=None):
        """
        General init

        :param url: url of TestRail, string, required
        :param email: email of TestRail user with proper access rights, string, required
        :param password: password of TestRail user with proper access rights, string, required
        :param priority: default priority level for testcases, integer, usually it's "4" within following list:
                                                                                  ['Low', 'Medium', 'High', 'Critical']
        :param project: project id, integer, required
        :param type_platforms: list of dicts, with sections ids, where dict = {'name': 'UI',
                                                                               'sections': [16276]}
        :param automation_platforms: list of dicts of automation platforms, dict = {'name': 'Desktop Chrome',
                                                                                    'internal_name': 'type_id',
                                                                                    'sections': [16276]}
        :param suite_id: suite id, integer, optional, if no suite-management is activated
        :param debug: debug output is enabled, may be True or False, optional
        """
        if debug:
            print("\nAT Coverage Reporter init")
        if url is None or email is None or password is None:
            raise ValueError("No TestRails credentials are provided!")
        else:
            pass
        self.__debug = debug if debug is not None else True
        self.__automation_platforms = automation_platforms  # should be passed with specific TestRails sections
        self.__type_platforms = type_platforms  # should be passed with specific TestRails sections
        self.__project = project
        self.__priority = priority
        self.__api = TestRailAPI(url=url, email=email, password=password)
        self.__suite_id = suite_id

    def __get_sections(self, parent_list: list, project=None, suite_id=None):
        """
        Wrapper to get all sections ids of TestRails project/suite

        :param parent_list: list for all sections, initially top section should be passed
        :param project: project id, integer, required
        :param suite_id: suite id, integer, optional, if no suite-management is activated
        :return: list with ids all of sections
        """
        project = project if project else self.__project
        suite_id = suite_id if suite_id else self.__suite_id
        if not project:
            raise ValueError("No project specified, report aborted!")
        all_sections = self.__get_all_sections(project_id=project, suite_id=suite_id)
        for section in all_sections:
            if section['parent_id'] in parent_list:
                parent_list.append(section['id'])
        return parent_list

    def __get_all_sections(self, project_id=None, suite_id=None, debug=None):
        """
        Wrapper to get all sections of TestRails project/suite

        :param project_id: project id, integer, required
        :param suite_id: suite id, integer, optional, if no suite-management is activated
        :param debug: debug output is enabled, may be True or False, optional
        :return: list, contains all of sections
        """
        project = project_id if project_id else self.__project
        suite_id = suite_id if suite_id else self.__suite_id
        debug = debug if debug is not None else self.__debug
        sections = []
        if not project:
            raise ValueError("No project specified, report aborted!")
        first_run = True
        criteria = None
        response = None
        while criteria is not None or first_run:
            if first_run:
                try:
                    response = self.__api.sections.get_sections(project_id=project, suite_id=suite_id)
                except Exception as e:
                    print(f"Get sections failed. Please validate your settings!\nError{format_error(e)}")
                    return None
                first_run = False
            elif response['_links']['next'] is not None:
                response = self.__api.sections.get_sections(project_id=project, suite_id=suite_id,
                                                            offset=int(response['_links']['next'].split("&offset=")[1]))
            sections = sections + response['sections']
            criteria = response['_links']['next']
        if debug:
            print(f'Found {len(sections)} existing sections in TestRails for project {project_id}, suite {suite_id}')
        return sections

    def __get_all_cases(self, project_id=None, suite_id=None, section_id=None, priority_id=None, debug=None):
        """
        Wrapper to get all test cases for selected project, suite, section and priority

        :param project_id: project id, integer, required
        :param suite_id: suite id, integer, optional, if no suite-management is activated
        :param section_id: section id, integer, section where testcases should be found, optional
        :param priority_id: priority, list of integers, id of priority for test case to search
        :param debug: debug output is enabled, may be True or False, optional
        :return: list with all cases
        """
        project_id = project_id if project_id else self.__project
        suite_id = suite_id if suite_id else self.__suite_id
        debug = debug if debug is not None else self.__debug
        cases_list = []
        first_run = True
        criteria = None
        response = None
        while criteria is not None or first_run:
            if first_run:
                try:
                    response = self.__api.cases.get_cases(project_id=project_id, suite_id=suite_id,
                                                          section_id=section_id, priority_id=priority_id)
                except Exception as e:
                    raise ValueError(f"Get cases failed. Please validate your settings!\nError{format_error(e)}")
                first_run = False
            elif response['_links']['next'] is not None:
                offset = int(response['_links']['next'].split("&offset=")[1].split("&")[0])
                response = self.__api.cases.get_cases(project_id=project_id, suite_id=suite_id,
                                                      section_id=section_id, priority_id=priority_id, offset=offset)
            cases_list = cases_list + response['cases']
            criteria = response['_links']['next']

        if debug:
            print(f'Found {len(cases_list)} existing tests in TestRails for project {project_id}, suite {suite_id}, '
                  f'section {section_id}, priority {priority_id}')
        return cases_list

    def automation_state_report(self, priority=None, project=None, automation_platforms=None,
                                filename_pattern='current_automation', suite=None, debug=None):
        """
        Generates data of automation coverage for stacked bar chart or staked line chart
        with values "Automated", "Not automated", "N/A". This distribution generated using values form fields
        with "internal_name" for specific parent section(s)

        :param priority: priority, list of integers, id of priority for test case to search
        :param project: project id, integer, required
        :param automation_platforms: list of dicts of automation platforms, dict = {'name': 'Desktop Chrome',
                                                                                    'internal_name': 'type_id',
                                                                                    'sections': [16276]}
        :param filename_pattern: pattern for filename, string
        :param suite: suite id, integer, optional, if no suite-management is activated
        :param debug: debug output is enabled, may be True or False, optional
        :return: list of results in CaseStat format
        """
        project = project if project else self.__project
        suite = suite if suite else self.__suite_id
        priority = priority if priority else self.__priority
        automation_platforms = automation_platforms if automation_platforms else self.__automation_platforms
        if not project:
            raise ValueError("No project specified, report aborted!")
        if not priority:
            raise ValueError("No critical priority specified, report aborted!")
        if not automation_platforms:
            raise ValueError("No automation platforms specified, report aborted!")
        debug = debug if debug is not None else self.__debug
        if debug:
            print('=== Staring generation of report for current automation state ===')
        index = 0
        results = []
        for platform in automation_platforms:
            if debug:
                print('processing platform ' + platform['name'])
            results.append(CaseStat(platform['name']))
            sections = self.__get_sections(platform['sections'])
            for section in sections:
                if debug:
                    print('passing section '+str(section))
                cases = self.__get_all_cases(project_id=project, suite_id=suite, section_id=section,
                                             priority_id=priority)
                results[index].set_total(results[index].get_total()+len(cases))
                for case in cases:
                    if (case[platform['internal_name']] == 2 and platform['internal_name'] != 'type_id') \
                            or (case[platform['internal_name']] == 3 and platform['internal_name'] == 'type_id'):
                        results[index].set_automated(results[index].get_automated()+1)
                    else:
                        if case[platform['internal_name']] == 3 and platform['internal_name'] != 'type_id':
                            results[index].set_na(results[index].get_na()+1)
            results[index].set_not_automated(results[index].get_total() - results[index].get_automated() -
                                             results[index].get_na())
            # save history data
            filename = f"{filename_pattern}_{results[index].get_name().replace(' ', '_')}.csv"
            CSVParser(debug=debug, filename=filename).save_history_data(report=results[index])
            index += 1
        return results
    
    def test_case_by_priority(self, project=None, suite=None, debug=None):
        """
        Generates data for pie/line chart with priority distribution

        :param project: project id, integer, required
        :param suite: suite id, integer, optional, if no suite-management is activated
        :param debug: debug output is enabled, may be True or False, optional
        :return: list with values (int) for bar chart
        """
        debug = debug if debug is not None else self.__debug
        project = project if project else self.__project
        suite = suite if suite else self.__suite_id
        if not project:
            raise ValueError("No project specified, report aborted!")
        if debug:
            print('=== Staring generation of report for test case priority distribution ===')
        results = []
        for i in range(1, 5):
            if debug:
                print(f'passing priority {str(i)}')
            results.append(len(self.__get_all_cases(project_id=project, suite_id=suite, priority_id=str(i))))
        return results
    
    def test_case_by_type(self, project=None, type_platforms=None, filename_pattern='current_area_distribution',
                          suite=None, debug=None):
        """
        Generates data for pie/line chart with distribution by type of platforms (guided by top section).

        :param project: project id, integer, required
        :param type_platforms: list of dicts, with sections ids, where dict = {'name': 'UI',
                                                                               'sections': [16276]}
        :param filename_pattern: pattern for filename, string
        :param suite: suite id, integer, optional, if no suite-management is activated
        :param debug: debug output is enabled, may be True or False, optional
        :return: list with values (int) for bar chart
        """
        type_platforms = type_platforms if type_platforms else self.__type_platforms
        project = project if project else self.__project
        suite = suite if suite else self.__suite_id
        if not project:
            raise ValueError("No project specified, report aborted!")
        if not type_platforms:
            raise ValueError("No platform types are provided, report aborted!")
        debug = debug if debug is not None else self.__debug
        project = project if project else self.__project
        if debug:
            print('=== Staring generation of report for test case area distribution ===')
        index = 0
        results = []
        for platform in type_platforms:
            if debug:
                print('processing area ' + platform['name'])
            results.append(CaseStat(platform['name']))
            sections = self.__get_sections(platform['sections'])
            for section in sections:
                if debug:
                    print('passing section '+str(section))
                cases = self.__get_all_cases(project_id=project, suite_id=suite, section_id=section)
                results[index].set_total(results[index].get_total()+len(cases))
            # save history data
            filename = f"{filename_pattern}_{results[index].get_name().replace(' ', '_')}.csv"
            CSVParser(debug=debug, filename=filename).save_history_data(report=results[index])
            index += 1
        return results
