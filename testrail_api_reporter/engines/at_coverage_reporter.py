# -*- coding: utf-8 -*-
""" Engine to generate obtain TestRail data and prepare reports """

from requests.exceptions import ReadTimeout
from testrail_api import TestRailAPI  # type: ignore

from ..utils.case_stat import CaseStat
from ..utils.csv_parser import CSVParser
from ..utils.logger_config import setup_logger, DEFAULT_LOGGING_LEVEL
from ..utils.reporter_utils import format_error, init_get_cases_process


class ATCoverageReporter:
    """Class for data generator for automation coverage reports (or similar data) from TestRails"""

    def __init__(
        self,
        url: str,
        email: str,
        password: str,
        priority=None,
        project=None,
        type_platforms=None,
        automation_platforms=None,
        suite_id=None,
        logger=None,
        log_level=DEFAULT_LOGGING_LEVEL,
    ):
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
                                                                                    'sections': [16276],
                                                                                    'auto_code': 3,
                                                                                    'na_code': 4}
        :param suite_id: suite id, integer, optional, if no suite-management is activated
        :param logger: logger object, optional
        :param log_level: logging level, optional, by default is logging.DEBUG
        """
        if not logger:
            self.___logger = setup_logger(name="ATCoverageReporter", log_file="ATCoverageReporter.log", level=log_level)
        else:
            self.___logger = logger
        self.___logger.debug("Initializing AT Coverage Reporter")
        if url is None or email is None or password is None:
            raise ValueError("No TestRails credentials are provided!")
        self.__automation_platforms = automation_platforms  # should be passed with specific TestRails sections
        self.__type_platforms = type_platforms  # should be passed with specific TestRails sections
        self.__project = project
        self.__priority = priority
        self.__api = TestRailAPI(url=url, email=email, password=password)
        self.__suite_id = suite_id

    def __get_sections(self, parent_list: list, project=None, suite_id=None):
        """
        Wrapper to get all sections ids of TestRails project/suite

        :param parent_list: list for all sections, initially a top section should be passed
        :param project: project id, integer, required
        :param suite_id: suite id, integer, optional, an if no suite-management is activated
        :return: list with ids all the sections
        """
        project = project if project else self.__project
        suite_id = suite_id if suite_id else self.__suite_id
        if not project:
            raise ValueError("No project specified, report aborted!")
        all_sections = self.__get_all_sections(project_id=project, suite_id=suite_id)
        for section in all_sections:
            if section["parent_id"] in parent_list:
                parent_list.append(section["id"])
        return parent_list

    def __get_all_sections(self, project_id=None, suite_id=None):
        """
        Wrapper to get all sections of TestRails project/suite

        :param project_id: project id, integer, required
        :param suite_id: suite id, integer, optional, if no suite-management is activated
        :return: list, contains all the sections
        """
        project = project_id if project_id else self.__project
        suite_id = suite_id if suite_id else self.__suite_id
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
                except Exception as error:  # pylint: disable=broad-except
                    self.___logger.error(
                        "Get sections failed. Please validate your settings!\nError%s", format_error(error)
                    )
                    return None
                first_run = False
            elif response["_links"]["next"] is not None:  # pylint: disable=unsubscriptable-object
                offset = int(
                    response["_links"]["next"]  # pylint: disable=unsubscriptable-object
                    .partition("offset=")[2]
                    .partition("&")[0]
                )
                response = self.__api.sections.get_sections(project_id=project, suite_id=suite_id, offset=offset)
            sections = sections + response["sections"]  # pylint: disable=unsubscriptable-object
            criteria = response["_links"]["next"]  # pylint: disable=unsubscriptable-object
        self.___logger.debug(
            "Found %s existing sections in TestRails for project %s, suite %s", len(sections), project, suite_id
        )
        return sections

    def __get_all_cases(
        self,
        project_id=None,
        suite_id=None,
        section_id=None,
        priority_id=None,
        retries=3,
    ):
        """
        Wrapper to get all test cases for selected project, suite, section and priority

        :param project_id: project id, integer, required
        :param suite_id: suite id, integer, optional, if no suite-management is activated
        :param section_id: section id, integer, section where testcases should be found, optional
        :param priority_id: priority, list of integers, id of priority for test case to search
        :param retries: number of retries, integer, optional
        :return: list with all cases
        """
        project_id = project_id if project_id else self.__project
        suite_id = suite_id if suite_id else self.__suite_id
        cases_list, first_run, criteria, response, retry = init_get_cases_process()
        while criteria is not None or first_run:
            if first_run:
                try:
                    response = self.__api.cases.get_cases(
                        project_id=project_id,
                        suite_id=suite_id,
                        section_id=section_id,
                        priority_id=priority_id,
                    )
                except ReadTimeout as error:
                    if retry < retries:
                        retry += 1
                        self.___logger.debug("Timeout error, retrying %s/%s...", retry, retries)
                        continue
                    raise ValueError(
                        f"Get cases failed. Please validate your settings!\nError{format_error(error)}"
                    ) from error
                except Exception as error:  # pylint: disable=broad-except
                    raise ValueError(
                        f"Get cases failed. Please validate your settings!\nError{format_error(error)}"
                    ) from error
                first_run = False
                retry = 0
            elif response["_links"]["next"] is not None:  # pylint: disable=unsubscriptable-object
                offset = int(
                    response["_links"]["next"]  # pylint: disable=unsubscriptable-object
                    .partition("offset=")[2]
                    .partition("&")[0]
                )
                try:
                    response = self.__api.cases.get_cases(
                        project_id=project_id,
                        suite_id=suite_id,
                        section_id=section_id,
                        priority_id=priority_id,
                        offset=offset,
                    )
                except ReadTimeout as error:
                    if retry < retries:
                        retry += 1
                        self.___logger.debug("Timeout error, retrying %s/%s...", retry, retries)
                        continue
                    raise ValueError(
                        f"Get cases failed. Please validate your settings!\nError{format_error(error)}"
                    ) from error
                except Exception as error:
                    raise ValueError(
                        f"Get cases failed. Please validate your settings!\nError{format_error(error)}"
                    ) from error
                retry = 0

            cases_list = cases_list + response["cases"]  # pylint: disable=unsubscriptable-object
            criteria = response["_links"]["next"]  # pylint: disable=unsubscriptable-object

        self.___logger.debug(
            "Found %s existing tests in TestRails for project %s, suite %s, section %s, priority %s",
            len(cases_list),
            project_id,
            suite_id,
            section_id,
            priority_id,
        )
        return cases_list

    def automation_state_report(
        self,
        priority=None,
        project=None,
        automation_platforms=None,
        filename_pattern="current_automation",
        suite=None,
    ):
        """
        Generates data of automation coverage for stacked bar chart or staked line chart
        with values "Automated", "Not automated", "N/A". This distribution generated using values form fields
        with "internal_name" for specific parent section(s)

        :param priority: priority, list of integers, id of priority for test case to search
        :param project: project id, integer, required
        :param automation_platforms: list of dicts of automation platforms, dict = {'name': 'Desktop Chrome',
                                                                                    'internal_name': 'type_id',
                                                                                    'sections': [16276],
                                                                                    'auto_code': 3,
                                                                                    'na_code': 4}
        :param filename_pattern: pattern for filename, string
        :param suite: suite id, integer, optional, if no suite-management is activated
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
        self.___logger.debug("=== Starting generation of report for current automation state ===")
        index = 0
        results = []
        for platform in automation_platforms:
            self.___logger.debug("Processing platform %s", platform["name"])
            results.append(CaseStat(platform["name"]))
            sections = self.__get_sections(platform["sections"])
            for section in sections:
                self.___logger.debug(" Passing section %s", section)
                cases = self.__get_all_cases(
                    project_id=project,
                    suite_id=suite,
                    section_id=section,
                    priority_id=priority,
                )
                results[index].set_total(results[index].get_total() + len(cases))
                for case in cases:
                    if case[platform["internal_name"]] == platform["auto_code"]:
                        results[index].set_automated(results[index].get_automated() + 1)
                    else:
                        if case[platform["internal_name"]] == platform["na_code"]:
                            results[index].set_not_applicable(results[index].get_not_applicable() + 1)
            results[index].set_not_automated(
                results[index].get_total() - results[index].get_automated() - results[index].get_not_applicable()
            )
            # save history data
            filename = f"{filename_pattern}_{results[index].get_name().replace(' ', '_')}.csv"
            CSVParser(log_level=self.___logger.level, filename=filename).save_history_data(report=results[index])
            index += 1
        return results

    def test_case_by_priority(self, project=None, suite=None):
        """
        Generates data for pie/line chart with priority distribution

        :param project: project id, integer, required
        :param suite: suite id, integer, optional, if no suite-management is activated
        :return: list with values (int) for bar chart
        """
        project = project if project else self.__project
        suite = suite if suite else self.__suite_id
        if not project:
            raise ValueError("No project specified, report aborted!")
        self.___logger.debug("=== Starting generation of report for test case priority distribution ===")
        results = []
        for i in range(1, 5):
            self.___logger.debug("Processing priority %s", str(i))
            results.append(len(self.__get_all_cases(project_id=project, suite_id=suite, priority_id=str(i))))
        return results

    def test_case_by_type(
        self,
        project=None,
        type_platforms=None,
        filename_pattern="current_area_distribution",
        suite=None,
    ):
        """
        Generates data for pie/line chart with distribution by type of platforms (guided by top section).

        :param project: project id, integer, required
        :param type_platforms: list of dicts, with sections ids, where dict = {'name': 'UI',
                                                                               'sections': [16276]}
        :param filename_pattern: pattern for filename, string
        :param suite: suite id, integer, optional, if no suite-management is activated
        :return: list with values (int) for bar chart
        """
        type_platforms = type_platforms if type_platforms else self.__type_platforms
        project = project if project else self.__project
        suite = suite if suite else self.__suite_id
        if not project:
            raise ValueError("No project specified, report aborted!")
        if not type_platforms:
            raise ValueError("No platform types are provided, report aborted!")
        project = project if project else self.__project
        self.___logger.debug("=== Starting generation of report for test case type distribution ===")
        index = 0
        results = []
        for platform in type_platforms:
            self.___logger.debug("Processing platform %s", platform["name"])
            results.append(CaseStat(platform["name"]))
            sections = self.__get_sections(platform["sections"])
            for section in sections:
                self.___logger.debug(" Passing section %s", section)
                cases = self.__get_all_cases(project_id=project, suite_id=suite, section_id=section)
                results[index].set_total(results[index].get_total() + len(cases))
            # save history data
            filename = f"{filename_pattern}_{results[index].get_name().replace(' ', '_')}.csv"
            CSVParser(log_level=self.___logger.level, filename=filename).save_history_data(report=results[index])
            index += 1
        return results
