from xmltodict import parse
from testrail_api import TestRailAPI
from os.path import exists
import datetime


class TestRailResultsReporter:
    def __init__(self, url, email, password, project_id, xml_report='junit-report.xml', suite_id=None):
        self.__api = TestRailAPI(url, email, password)
        self.__xml_report = xml_report if self.__check_report_exists(xml_report=xml_report) else None
        self.__project_id = project_id if self.__check_project(project_id=project_id) else None
        self.__suite_id = suite_id if self.__check_suite(suite_id=suite_id) else None
        self.__at_section = self.__ensure_automation_section() if self.__project_id and self.__suite_id else None
        self.__check_section()
        self.__timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    def __xml_to_dict(self, filename='junit-report.xml'):
        with open(filename, 'r', encoding='utf-8') as file:
            xml = file.read()

        list_of_cases = []

        parsed_xml = parse(xml)
        self.__timestamp = parsed_xml['testsuites']['testsuite']['@timestamp'].split(".")[0]

        for item in parsed_xml['testsuites']['testsuite']['testcase']:
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
        print(f'Fund test run at {self.__timestamp}, found {len(list_of_cases)} test results')
        return list_of_cases

    @staticmethod
    def __search_for_item(searched_value, list_to_seek, field):
        for item in list_to_seek:
            if item[field] == searched_value:
                return item

        return [element for element in list_to_seek if element[field] == searched_value]

    def __ensure_automation_section(self, title="pytest"):
        response = self.__api.sections.get_sections(project_id=self.__project_id, suite_id=self.__suite_id)
        first_run = True
        item_id = None
        while response['_links']['next'] is not None or first_run:
            sections = response['sections']
            for item in sections:
                if item['name'] == title:
                    item_id = item['id']
            if response['_links']['next'] is not None:
                response = self.__api.sections.get_sections(project_id=self.__project_id, suite_id=self.__suite_id,
                                                            offset=int(response['_links']['next'].split("&offset=")[1]))
            first_run = False if first_run else True
        if not item_id:
            item_id = self.__api.sections.add_section(project_id=self.__project_id, name=title)['id']
            print("No default automation folder is found, created new one with name'{title}'")
        return item_id

    def __enrich_with_tc_num(self, xml_dict_list, tc_dict_list):
        enriched_list = []
        missed_tests_counter = 0
        for item in xml_dict_list:
            cases = self.__search_for_item(searched_value=item['automation_id'], list_to_seek=tc_dict_list,
                                           field='custom_automation_id')
            if not cases:
                cases = [self.__api.cases.add_case(section_id=self.__at_section, title=item['automation_id'],
                                                   custom_automation_id=item['automation_id'])]
                missed_tests_counter = missed_tests_counter + 1
            if isinstance(cases, list):
                for case in cases:
                    enriched_list.append({'case_id': case['id'], 'status_id': item['status'], 'comment': '',
                                          'elapsed': item['time'], 'attachments': []})
            else:
                elapsed = int(item["time"].split(".")[0])
                elapsed = elapsed if elapsed > 0 else elapsed + 1
                comment = item['message'] if 'failure' in item.keys() else ''
                enriched_list.append(
                    {'case_id': cases['id'], 'status_id': item['status'], 'comment': comment,
                     'elapsed': f'{elapsed}s', 'attachments': []})
        if missed_tests_counter:
            print(f"{missed_tests_counter} test cases were missed, they was automatically created.")
        print(f"{len(enriched_list)} test results were prepared for send.")
        return enriched_list

    def __get_all_auto_cases(self):
        cases_list = []
        response = self.__api.cases.get_cases(project_id=self.__project_id, suite_id=self.__suite_id)
        first_run = True
        while response['_links']['next'] is not None or first_run:
            cases = response['cases']
            for item in cases:
                if item['custom_automation_id'] is not None:
                    cases_list.append({'id': item['id'], 'custom_automation_id': item['custom_automation_id']})
            if response['_links']['next'] is not None:
                response = self.__api.cases.get_cases(project_id=self.__project_id, suite_id=self.__suite_id,
                                                      offset=int(response['_links']['next'].split("&offset=")[1]))
            first_run = False if first_run else True

        print(f'Found {len(cases_list)} existing tests in TestRails with automation_id')
        return cases

    def __prepare_payload(self):
        parsed_xml = self.__xml_to_dict(filename=self.__xml_report)
        parsed_cases = self.__get_all_auto_cases()
        payload = self.__enrich_with_tc_num(xml_dict_list=parsed_xml, tc_dict_list=parsed_cases)
        return payload

    def __prepare_title(self, environment=None, timestamp=None):
        if timestamp is None:
            timestamp = self.__timestamp
        title = f"AT run {timestamp}"
        if environment:
            title = f"{title} on {environment}"
        return title

    def send_results(self, run_id=None, environment=None, title=None, timestamp=None, close_run=True):
        if not (self.__check_project() and self.__check_suite() and self.__check_section() and self.__xml_report):
            return True
        if not title:
            title = self.__prepare_title(environment, timestamp)
        payload = self.__prepare_payload()
        cases_list = []
        for item in payload:
            cases_list.append(item['case_id'])
        if not run_id:
            print(f"Creating new test run '{title}'")
            run_id = self.__api.runs.add_run(project_id=self.__project_id, suite_id=self.__suite_id, name=title,
                                             include_all=False, case_ids=cases_list)['id']
        self.__api.results.add_results_for_cases(run_id=run_id, results=self.__prepare_payload())
        if close_run:
            self.__api.runs.close_run(run_id=run_id)
            print(f"Test run '{title}' is closed")
        print(f"{len(cases_list)} results were added to test run '{title}', cases updated. Done")
        return False

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
        retval = True
        project_id = self.__project_id if not project_id else project_id
        try:
            self.__api.projects.get_project(project_id=project_id)
        except Exception as e:
            print(f"Error {e.args[0]}. No such project is found, please set valid project ID")
            retval = False
        return retval

    def __check_suite(self, suite_id=None):
        retval = True
        suite_id = self.__suite_id if not suite_id else suite_id
        try:
            self.__api.suites.get_suite(suite_id=suite_id)
        except Exception as e:
            print(f"Error {e.args[0]}. No such suite is found, please set valid AT report section")
            retval = False
        return retval

    def __check_section(self, section_id=None):
        retval = True
        section_id = self.__at_section if not section_id else section_id
        try:
            self.__api.sections.get_section(section_id=section_id)
        except Exception as e:
            print(f"Error {e.args[0]}. No default section found, please set valid suite ID")
            retval = False
        return retval

    def __check_report_exists(self, xml_report=None):
        retval = True
        if not xml_report:
            xml_report = self.__xml_report
        if not exists(xml_report):
            print(f"Error 404. No XML file is found. Please specify correct path.")
            retval = False
        return retval
