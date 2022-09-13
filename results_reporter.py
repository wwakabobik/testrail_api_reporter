import datetime
from os.path import exists

from xmltodict import parse
from testrail_api import TestRailAPI

from .reporter_utils import format_error


class TestRailResultsReporter:
    """ Reporter to TestRails from xml report results, obtained by pytest """
    def __init__(self, url: str, email: str, password: str, project_id: int, xml_report='junit-report.xml',
                 suite_id=None, debug=True):
        """
        Default init

        :param url: url of TestRail, string, required
        :param email: email of TestRail user with proper access rights, string, required
        :param password: password of TestRail user with proper access rights, string, required
        :param project_id: project id, integer, required
        :param xml_report: filename (maybe with path) of xml test report
        :param suite_id: suite id, integer, optional, if no suite-management is activated
        :param debug: debug output is enabled, may be True or False, optional
        """
        if debug:
            print("\nTestrail Api Reporter init")
        if url is None or email is None or password is None:
            raise ValueError("No TestRails credentials are provided!")
        else:
            self.__api = TestRailAPI(url, email, password)
        self.__xml_report = xml_report if self.__check_report_exists(xml_report=xml_report) else None
        self.__project_id = project_id if self.__check_project(project_id=project_id) else None
        self.__suite_id = suite_id if self.__check_suite(suite_id=suite_id) else None
        self.__at_section = self.__ensure_automation_section() if self.__project_id else None
        self.__check_section(section_id=self.__at_section)
        self.__timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        self.__debug = debug

    def __xml_to_dict(self, filename='junit-report.xml'):
        """
        Converts xml file to python dict
        :param filename: filename, string, maybe with path
        :return: dict with list of cases
        """
        if not self.__check_report_exists(xml_report=self.__xml_report):
            return None
        with open(filename, 'r', encoding='utf-8') as file:
            xml = file.read()

        list_of_cases = []

        parsed_xml = parse(xml)
        self.__timestamp = parsed_xml['testsuites']['testsuite']['@timestamp'].split(".")[0]

        cases = parsed_xml['testsuites']['testsuite']['testcase']
        cases = cases if isinstance(cases, list) else [cases]
        for item in cases:
            status = 1
            if 'failure' in item.keys():
                status = 5
            if 'skipped' in item.keys():
                if item['skipped']['@type'] == 'pytest.xfail':
                    status = 5
                else:
                    status = 7
            list_of_cases.append({'automation_id': f'{item["@classname"]}.{item["@name"]}',
                                  'time': item["@time"],
                                  'status': status,
                                  'message': f'{item["failure"]["@message"]} : '
                                             f'{item["failure"]["#text"]}' if 'failure' in item.keys() else ''})
        print(f'Found test run at {self.__timestamp}, found {len(list_of_cases)} test results')
        return list_of_cases

    @staticmethod
    def __search_for_item(searched_value, list_to_seek, field):
        """
        Item seeker by value within list of dicts

        :param searched_value: value what we're looking for
        :param list_to_seek: list where we perform search
        :param field: field of list dict
        :return: element
        """
        for item in list_to_seek:
            if item[field] == searched_value:
                return item

        return [element for element in list_to_seek if element[field] == searched_value]

    def __ensure_automation_section(self, title="pytest"):
        """
        Service function, checks that special (default) placeholder for automation non-classified tests exists

        :param title: title for default folder, string
        :return: id of section
        """
        first_run = True
        item_id = None
        criteria = None
        response = None
        while criteria is not None or first_run:
            if first_run:
                try:
                    response = self.__api.sections.get_sections(project_id=self.__project_id, suite_id=self.__suite_id)
                except Exception as e:
                    print(f"Get sections failed. Please validate your settings!\nError{format_error(e)}")
                    self.__self_check()
                    return None
                first_run = False
            elif response['_links']['next'] is not None:
                response = self.__api.sections.get_sections(project_id=self.__project_id, suite_id=self.__suite_id,
                                                            offset=int(response['_links']['next'].split("&offset=")[1]))
            sections = response['sections']
            for item in sections:
                if item['name'] == title:
                    item_id = item['id']
            criteria = response['_links']['next']
        if not item_id:
            try:
                item_id = self.__api.sections.add_section(project_id=self.__project_id, suite_id=self.__suite_id,
                                                          name=title)['id']
            except Exception as e:
                print(f"Can't add section. Something nasty happened. Error{format_error(e)}")
                self.__self_check()
                return None
            print(f"No default automation folder is found, created new one with name'{title}'")
        return item_id

    def __enrich_with_tc_num(self, xml_dict_list, tc_dict_list):
        """
        Add test case id to case result

        :param xml_dict_list: list of dict, with test cases, obtained from xml report
        :param tc_dict_list: list of dict, with test cases, obtained from TestRails
        :return: enriched list of dict with test cases
        """
        enriched_list = []
        missed_tests_counter = 0
        for item in xml_dict_list:
            cases = self.__search_for_item(searched_value=item['automation_id'], list_to_seek=tc_dict_list,
                                           field='custom_automation_id')
            if not cases:
                try:
                    cases = [self.__api.cases.add_case(section_id=self.__at_section, title=item['automation_id'],
                                                       custom_automation_id=item['automation_id'])]
                except Exception as e:
                    print(f"Add case failed. Please validate your settings!\nError{format_error(e)}")
                    self.__self_check()
                    return None
                missed_tests_counter = missed_tests_counter + 1
            cases = cases if isinstance(cases, list) else [cases]
            for case in cases:
                comment = item['message'] if 'failure' in item.keys() else ''
                elapsed = item['time'].split(".")[0]
                elapsed = 1 if elapsed == 0 else elapsed
                enriched_list.append({'case_id': case['id'], 'status_id': item['status'], 'comment': comment,
                                      'elapsed': elapsed, 'attachments': []})
        if missed_tests_counter:
            print(f"{missed_tests_counter} test cases were missed, they was automatically created.")
        print(f"{len(enriched_list)} test results were prepared for send.")
        return enriched_list

    def __get_all_auto_cases(self):
        """
        Collects all test cases from TestRails with non-empty automation_id

        :return: list of dict with cases
        """
        cases_list = []
        first_run = True
        criteria = None
        response = None
        while criteria is not None or first_run:
            if first_run:
                try:
                    response = self.__api.cases.get_cases(project_id=self.__project_id, suite_id=self.__suite_id)
                except Exception as e:
                    print(f"Get cases failed. Please validate your settings!\nError{format_error(e)}")
                    self.__self_check()
                    return None
                first_run = False
            elif response['_links']['next'] is not None:
                offset = int(response['_links']['next'].split("&offset=")[1].split("&")[0])
                response = self.__api.cases.get_cases(project_id=self.__project_id, suite_id=self.__suite_id,
                                                      offset=offset)
            cases = response['cases']
            for item in cases:
                if item['custom_automation_id'] is not None:
                    cases_list.append({'id': item['id'], 'custom_automation_id': item['custom_automation_id']})
            criteria = response['_links']['next']

        print(f'Found {len(cases_list)} existing tests in TestRails with automation_id')
        return cases_list

    def __prepare_payload(self):
        """
        Prepares payload from xml report for sending to TestRails

        :return: payload in proper format (list of dicts)
        """
        parsed_xml = self.__xml_to_dict(filename=self.__xml_report)
        parsed_cases = self.__get_all_auto_cases()
        if not parsed_xml or not parsed_cases:
            print("Preparation of payload failed, aborted")
            return None
        payload = self.__enrich_with_tc_num(xml_dict_list=parsed_xml, tc_dict_list=parsed_cases)
        return payload

    def __prepare_title(self, environment=None, timestamp=None):
        """
        Format test run name based on input string (most probably environment) and timestamp

        :param environment: some string identifier of run
        :param timestamp: custom timestamp
        :return: string of prepared string for AT run name
        """
        if timestamp is None:
            timestamp = self.__timestamp
        title = f"AT run {timestamp}"
        if environment:
            title = f"{title} on {environment}"
        return title

    def send_results(self, run_id=None, environment=None, title=None, timestamp=None, close_run=True, run_name=None,
                     delete_old_run=False):
        """
        Send results to TestRail

        :param run_id: specific run id, if any, optional
        :param environment: custom name pattern for run name, optional
        :param title: custom title, if provided, will be used as priority, optional
        :param timestamp: custom timestamp, optional
        :param close_run: close or not run, True or False
        :param run_name: name of test run, will be used if provided at top priority
        :param delete_old_run: delete or not previous run if old one exists with same name
        :return: run id where results were submitted
        """
        print("\n")
        if not self.__project_id or not self.__at_section \
                or not self.__check_report_exists(xml_report=self.__xml_report):
            print("Error! Please specify all required params!")
            self.__self_check()
            return True
        title = self.__prepare_title(environment, timestamp) if not title else title
        title = run_name if run_name else title
        payload = self.__prepare_payload()
        run_id = self.__prepare_runs(cases=payload, title=title, run_id=run_id, run_name=run_name,
                                     delete_run=delete_old_run)
        retval = self.__add_results(run_id=run_id, results=payload)
        if close_run:
            self.__close_run(run_id=run_id, title=title)
        print(f"{len(payload)} results were added to test run '{title}', cases updated. Done")
        return retval

    def set_project_id(self, project_id):
        self.__project_id = project_id if self.__check_project(project_id=project_id) else None

    def set_suite_id(self, suite_id):
        if self.__check_project():
            self.__suite_id = suite_id if self.__check_suite(suite_id=suite_id) else None

    def set_xml_filename(self, xml_filename):
        self.__xml_report = xml_filename if self.__check_report_exists(xml_report=xml_filename) else None

    def set_at_report_section(self, section_name):
        if self.__check_project() and self.__check_suite():
            self.__at_section = self.__ensure_automation_section(title=section_name)

    def set_timestamp(self, new_timestamp):
        self.__timestamp = new_timestamp

    def __check_project(self, project_id=None):
        """
        Check that the project exists

        :param project_id: project id, integer
        :return: True or False
        """
        retval = True
        try:
            self.__api.projects.get_project(project_id=project_id)
        except Exception as e:
            print(f"No such project is found, please set valid project ID.\nError{format_error(e)}")
            retval = False
        return retval

    def __check_suite(self, suite_id=None):
        """
        Check that the suite exists

        :param suite_id: id of suite, integer
        :return: True or False
        """
        retval = True
        try:
            self.__api.suites.get_suite(suite_id=suite_id)
        except Exception as e:
            print(f"No such suite is found, please set valid AT report section.\nError{format_error(e)}")
            retval = False
        return retval

    def __check_section(self, section_id=None):
        """
        Check that the section exists

        :param section_id: id of suite, integer
        :return: True or False
        """
        retval = True
        try:
            self.__api.sections.get_section(section_id=section_id)
        except Exception as e:
            print(f"No default section found, please set valid suite ID.\nError{format_error(e)}")
            retval = False
        return retval

    def __check_report_exists(self, xml_report=None):
        """
        Check that the xml report exists

        :param xml_report: filename of the xml report, maybe with path
        :return: True or False
        """
        retval = False
        if not xml_report:
            xml_report = self.__xml_report
        if xml_report:
            if exists(xml_report):
                retval = True
        if not retval:
            print(f"Please specify correct path.\nError 404: No XML file found")
        return retval

    def __check_run_exists(self, run_id=None):
        """
        Check that the run exists

        :param run_id: id of suite, integer
        :return: True or False
        """
        retval = True
        try:
            self.__api.runs.get_run(run_id=run_id)
        except Exception as e:
            print(f"No specified run found, please use correct one or use default (None)."
                  f"\nError{format_error(e)}")
            retval = False
        return retval

    def __self_check(self):
        """
        Health checker, calls checks
        """
        self.__check_project(project_id=self.__project_id)
        self.__check_suite(suite_id=self.__suite_id)
        self.__check_section(section_id=self.__at_section)
        self.__check_report_exists(xml_report=self.__xml_report)

    def __search_for_run_by_name(self, title=None):
        """
        Search run by name

        :param title: name of the run
        :return: run id, integer
        """
        retval = None
        first_run = True
        criteria = None
        while criteria is not None or first_run:
            if first_run:
                try:
                    response = self.__api.runs.get_runs(project_id=self.__project_id, suite_id=self.__suite_id)
                except Exception as e:
                    print(f"Can't get run list. Something nasty happened.\nError{format_error(e)}")
                    break
                first_run = False
            elif response['_links']['next'] is not None:
                offset = int(response['_links']['next'].split("&offset=")[1].split("&")[0])
                response = self.__api.runs.get_runs(project_id=self.__project_id, suite_id=self.__suite_id,
                                                    offset=offset)
            if response['runs']['name'] == title:
                retval = response['runs']['id']
                break
            criteria = response['_links']['next']
        return retval

    def __delete_run(self, run_id=None):
        """
        Delete run
        :param run_id: run id, integer
        :return: True if deleted, False in case of error
        """
        retval = True
        try:
            self.__api.runs.delete_run(run_id=run_id)
        except Exception as e:
            print(f"Can't delete run. Something nasty happened."
                  f"\nError{format_error(e)}")
            retval = False
        return retval

    def __add_run(self, title, cases_list=None, include_all=False):
        """
        Add a run

        :param title: title of run
        :param cases_list: test cases, which will be added to run
        :param include_all: every existing testcases may be included, by default - False
        :return: id of run, integer
        """
        retval = None
        print(f"Creating new test run '{title}'")
        try:
            retval = self.__api.runs.add_run(project_id=self.__project_id, suite_id=self.__suite_id, name=title,
                                             include_all=include_all, case_ids=cases_list)['id']
        except Exception as e:
            print(f"Add run failed. Please validate your settings!\nError{format_error(e)}")
            self.__self_check()
        return retval

    def __add_results(self, run_id=None, results=None):
        """
        Add results for test cases to TestRail
        :param run_id: run id
        :param results: payload (list of dicts)
        :return: run id or False in case of error
        """
        retval = False
        try:
            self.__api.results.add_results_for_cases(run_id=run_id, results=results)
            return run_id
        except Exception as e:
            print(f"Add results failed. Please validate your settings!\nError{format_error(e)}")
            self.__self_check()
            self.__check_run_exists(run_id=run_id)
        return retval

    def __prepare_runs(self, cases=None, title=None, run_id=None, run_name=None, delete_run=False):
        """
        Prepare run for submitting

        :param cases: list of cases, list of dicts
        :param title: title of test run (which will be submitted)
        :param run_id: run id
        :param run_name:
        :param delete_run: delete existing run or not (True or False), will be checked via run_name
        :return: run id
        """
        cases_list = []
        for item in cases:
            cases_list.append(item['case_id'])
        if run_name:
            run_id = self.__search_for_run_by_name(title=run_name)
            if not run_id:
                print("No run has been found by given name")
        if delete_run and run_id:
            self.__delete_run(run_id=run_id)
            run_id = None
        if not run_id:
            run_id = self.__add_run(title=title, cases_list=cases_list, include_all=False)
        return run_id

    def __close_run(self, title=None, run_id=None):
        """
        Closes run
        :param title: title of test run
        :param run_id: run id, integer
        :return: True or False
        """
        retval = True
        try:
            self.__api.runs.close_run(run_id=run_id)
            print(f"Test run '{title}' is closed")
        except Exception as e:
            print(f"Can't close run! Something nasty happened.\nError{format_error(e)}")
            retval = False
        return retval
