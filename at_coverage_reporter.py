from testrail_api import TestRailAPI

from csv_parser import CSVParser


class CaseStat:

    def __init__(self, name):
        self.name = name
        self.total = 0
        self.automated = 0
        self.not_automated = 0
        self.na = 0

    # getters
    def get_name(self):
        return self.name

    def get_total(self):
        return self.total

    def get_automated(self):
        return self.automated

    def get_not_automated(self):
        return self.not_automated

    def get_na(self):
        return self.na

    # setters
    def set_name(self, name):
        self.name = name

    def set_total(self, total):
        self.total = total

    def set_automated(self, automated):
        self.automated = automated

    def set_not_automated(self, not_automated):
        self.not_automated = not_automated

    def set_na(self, na):
        self.na = na
        
        
class ATCoverageReporter:
    def __init__(self, url, email, password, priority=None, project=None, type_platforms=None,
                 automation_platforms=None, debug=None, ):
        if debug:
            print("\nAT Coverage Reporter init")
        if url is None or email is None or password is None:
            raise Exception("No TestRails credentials are provided!")
        else:
            pass
        self.__debug = debug if debug is not None else True
        self.__automation_platforms = automation_platforms  # should be passed with specific TestRails sections
        self.__type_platforms = type_platforms  # should be passed with specific TestRails sections
        self.__project = project
        self.__priority = priority
        self.__api = TestRailAPI(url=url, email=email, password=password)
        self.__api.cases.get_cases()

    def __get_sections(self, parent_list, project=None, suite_id=None):
        project = project if project else self.__project
        if not project:
            raise "No project specified, report aborted!"
        all_sections = self.__api.sections.get_sections(project_id=project, suite_id=suite_id)
        for section in all_sections:
            if section['parent_id'] in parent_list:
                parent_list.append(section['id'])
        return parent_list

    def automation_state_report(self, priority=None, project=None, automation_platforms=None,
                                filename_pattern='current_automation', suite=None, debug=None):
        project = project if project else self.__project
        priority = priority if priority else self.__priority
        automation_platforms = automation_platforms if automation_platforms else self.__automation_platforms
        if not project:
            raise "No project specified, report aborted!"
        if not priority:
            raise "No critical priority specified, report aborted!"
        if not automation_platforms:
            raise "No automation platforms specified, report aborted!"
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
                cases = self.__api.cases.get_cases(project_id=project, suite_id=suite, section_id=section,
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
        debug = debug if debug is not None else self.__debug
        project = project if project else self.__project
        if not project:
            raise "No project specified, report aborted!"
        if debug:
            print('=== Staring generation of report for test case priority distribution ===')
        results = []
        for i in range(1, 5):
            if debug:
                print(f'passing priority {str(i)}')
            results.append(len(self.__api.cases.get_cases(project_id=project, suite_id=suite, priority_id=str(i))))
        return results
    
    def test_case_by_type(self, project=None, filename_pattern='current_area_distribution', suite=None, debug=True):
        debug = debug if debug is not None else self.__debug
        project = project if project else self.__project
        if not project:
            raise "No project specified, report aborted!"
        if debug:
            print('=== Staring generation of report for test case area distribution ===')
        index = 0
        results = []
        for platform in self.__type_platforms:
            if debug:
                print('processing area ' + platform['name'])
            results.append(CaseStat(platform['name']))
            sections = self.__get_sections(platform['sections'])
            for section in sections:
                if debug:
                    print('passing section '+str(section))
                cases = self.__api.cases.get_cases(project_id=project, suite_id=suite, section_id=section)
                results[index].set_total(results[index].get_total()+len(cases))
            # save history data
            filename = f"{filename_pattern}_{results[index].get_name().replace(' ', '_')}.csv"
            CSVParser(debug=debug, filename=filename).save_history_data(report=results[index])
            index += 1
        return results
