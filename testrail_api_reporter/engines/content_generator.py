# -*- coding: utf-8 -*-
"""Module for generating TestRail test case content (title, steps, docs) from automated tests via an AI provider"""

import ast
import json
import re
from os.path import relpath, splitext

from testrail_api import TestRailAPI

from ..utils.ai_providers import AIContentProvider
from ..utils.logger_config import setup_logger, DEFAULT_LOGGING_LEVEL
from ..utils.reporter_utils import DEFAULT_AUTOMATION_FIELD_NAME, format_error

DEFAULT_SYSTEM_PROMPT = """
You are a senior QA engineer. You will be given the source code of a single automated test \
(and optionally its docstring). Produce TestRail-ready test case documentation for it.
Respond ONLY with a JSON object (no markdown fences, no extra text) with the following keys:
{
  "title": "short, human-readable test case title",
  "preconditions": "preconditions required before the test can be run",
  "steps": "numbered test steps, as plain text",
  "expected_result": "expected result of the test",
  "description": "short description of what is covered and why"
}
Infer the steps and expected result from what the automated test actually asserts and does, \
do not invent behaviour that isn't exercised by the code.
"""

DEFAULT_FIELD_MAP = {
    "title": "title",
    "preconditions": "custom_preconds",
    "steps": "custom_steps",
    "expected_result": "custom_expected",
    "description": "custom_description",
}


class TestCaseContentGenerator:
    """Generates TestRail test case content from automated tests using a pluggable AI provider"""

    def __init__(
        self,
        url: str,
        email: str,
        password: str,
        project_id: int,
        provider: AIContentProvider,
        *,
        suite_id=None,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        automation_field_name=DEFAULT_AUTOMATION_FIELD_NAME,
        logger=None,
        log_level=DEFAULT_LOGGING_LEVEL,
    ):
        """
        Default init

        :param url: url of TestRail, string, required
        :param email: email of TestRail user with proper access rights, string, required
        :param password: password of TestRail user with proper access rights, string, required
        :param project_id: project id, integer, required
        :param provider: AI provider instance, used to generate content, required
        :param suite_id: suite id, integer, optional, if no suite-management is activated
        :param system_prompt: system prompt sent to the AI provider, string, optional
        :param automation_field_name: system name of the case custom field used to store the automation id,
                                       string. Defaults to 'custom_automation_id', which matches a custom field
                                       named 'automation_id' on older TestRail instances. Newer TestRail versions
                                       auto-prefix custom case fields created via the API with the entity name
                                       (e.g. a field named 'automation_id' becomes 'custom_case_automation_id') -
                                       check the actual system name via get_case_fields and pass it here if it
                                       differs from the default (see README for details)
        :param logger: logger object, optional
        :param log_level: logging level, optional, by default is 'logging.DEBUG'
        """
        if not logger:
            self.___logger = setup_logger(
                name="TestCaseContentGenerator", log_file="TestCaseContentGenerator.log", level=log_level
            )
        else:
            self.___logger = logger
        self.___logger.debug("Initializing TestCase Content Generator")
        if url is None or email is None or password is None:
            raise ValueError("No TestRails credentials are provided!")
        if provider is None:
            raise ValueError("No AI provider is provided!")
        self.__api = TestRailAPI(url, email, password)
        self.__provider = provider
        self.__project_id = project_id
        self.__suite_id = suite_id
        self.__system_prompt = system_prompt
        self.__automation_field_name = automation_field_name
        self.__cases_by_automation_id: dict = {}

    @staticmethod
    def __automation_id(file_path: str, qualified_name: str) -> str:
        """
        Build automation_id as 'path.to.testfile.filename.test_class.test_step'

        :param file_path: path to the python test file, string
        :param qualified_name: dotted name of class (if any) and test function, string
        :return: automation_id, string
        """
        module_path = splitext(relpath(file_path))[0].replace("/", ".").replace("\\", ".")
        return f"{module_path}.{qualified_name}"

    def extract_tests_from_file(self, file_path: str) -> list:
        """
        Parse a python test file and extract its test functions (standalone or inside classes)

        :param file_path: path to the python test file, string
        :return: list of dicts with keys: automation_id, name, docstring, source
        """
        with open(file_path, "r", encoding="utf-8") as source_file:
            source = source_file.read()
        tree = ast.parse(source, filename=file_path)
        tests = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name.startswith("test"):
                        tests.append(self.__describe_test(file_path, source, child, class_name=node.name))
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
                tests.append(self.__describe_test(file_path, source, node))
        self.___logger.debug("Extracted %s test(s) from %s", len(tests), file_path)
        return tests

    def __describe_test(self, file_path, source, node, class_name=None):
        """
        Build a dict describing a single test function

        :param file_path: path to the python test file, string
        :param source: full source of the file, string
        :param node: ast node of the test function, ast.FunctionDef
        :param class_name: name of the enclosing class, string, optional
        :return: dict with keys: automation_id, name, docstring, source
        """
        qualified_name = f"{class_name}.{node.name}" if class_name else node.name
        return {
            "automation_id": self.__automation_id(file_path, qualified_name),
            "name": node.name,
            "docstring": ast.get_docstring(node),
            "source": ast.get_source_segment(source, node),
        }

    def __build_prompt(self, test, extra_context=None):
        """
        Build a user prompt for a single test

        :param test: dict as returned by extract_tests_from_file, dict
        :param extra_context: extra free-form context to add to the prompt, string, optional
        :return: prompt, string
        """
        prompt = f"Test function: {test['name']}\n\n"
        if test.get("docstring"):
            prompt += f"Docstring:\n{test['docstring']}\n\n"
        prompt += f"Source code:\n```python\n{test['source']}\n```\n"
        if extra_context:
            prompt += f"\nAdditional context:\n{extra_context}\n"
        return prompt

    @staticmethod
    def __parse_response(response: str) -> dict:
        """
        Parse AI provider's response, tolerating markdown code fences around the JSON payload

        :param response: raw text returned by the AI provider, string
        :return: parsed dict
        """
        cleaned = re.sub(r"^```(?:json)?|```$", "", response.strip(), flags=re.MULTILINE).strip()
        return json.loads(cleaned)

    def generate_content(self, test: dict, extra_context=None) -> dict:
        """
        Generate TestRail content for a single extracted test

        :param test: dict as returned by extract_tests_from_file, dict
        :param extra_context: extra free-form context to add to the prompt, string, optional
        :return: dict with generated content (title, preconditions, steps, expected_result, description)
        """
        prompt = self.__build_prompt(test, extra_context=extra_context)
        response = self.__provider.generate(prompt=prompt, system_prompt=self.__system_prompt)
        try:
            content = self.__parse_response(response)
        except (json.JSONDecodeError, TypeError) as error:
            self.___logger.error(
                "Failed to parse AI provider response for %s\nError%s", test["automation_id"], format_error(error)
            )
            return {}
        self.___logger.debug("Generated content for %s", test["automation_id"])
        return content

    def generate_for_file(self, file_path: str, extra_context=None) -> list:
        """
        Extract tests from a file and generate TestRail content for each of them

        :param file_path: path to the python test file, string
        :param extra_context: extra free-form context to add to the prompt, string, optional
        :return: list of dicts with keys: automation_id, content
        """
        results = []
        for test in self.extract_tests_from_file(file_path):
            content = self.generate_content(test, extra_context=extra_context)
            results.append({"automation_id": test["automation_id"], "content": content})
        return results

    def __get_all_auto_cases(self) -> dict:
        """
        Collects all test cases from TestRail with non-empty automation_id, caches them by automation_id

        :return: dict, keyed by automation_id, values are case ids
        """
        if self.__cases_by_automation_id:
            return self.__cases_by_automation_id
        cases_by_automation_id: dict = {}
        first_run = True
        criteria = None
        response = None
        while criteria is not None or first_run:
            if first_run:
                try:
                    response = self.__api.cases.get_cases(project_id=self.__project_id, suite_id=self.__suite_id)
                except Exception as error:  # pylint: disable=broad-except
                    self.___logger.error(
                        "Get cases failed. Please validate your settings!\nError%s", format_error(error)
                    )
                    return {}
                first_run = False
            else:
                next_link = response["_links"]["next"]  # type: ignore  # pylint: disable=E1136
                offset = int(next_link.split("&offset=")[1].split("&")[0])
                response = self.__api.cases.get_cases(
                    project_id=self.__project_id, suite_id=self.__suite_id, offset=offset
                )
            for item in response["cases"]:  # type: ignore
                if item.get(self.__automation_field_name):
                    cases_by_automation_id[item[self.__automation_field_name]] = item["id"]
            criteria = response["_links"]["next"]  # type: ignore
        self.___logger.debug("Found %s test cases in TestRail with automation_id", len(cases_by_automation_id))
        self.__cases_by_automation_id = cases_by_automation_id
        return cases_by_automation_id

    @staticmethod
    def __map_fields(content: dict, field_map: dict) -> dict:
        """
        Map generated content keys to TestRail (custom) field names

        :param content: generated content, dict
        :param field_map: mapping of content key -> TestRail field name, dict
        :return: dict ready to be passed to TestRail's update_case
        """
        return {field_map[key]: value for key, value in content.items() if key in field_map and value is not None}

    def update_testrail_case(self, automation_id: str, content: dict, field_map=None):
        """
        Find TestRail case by automation_id and update it with generated content

        :param automation_id: automation_id of the test case, string
        :param content: generated content, as returned by generate_content, dict
        :param field_map: mapping of content key -> TestRail field name, dict, optional
        :return: updated case dict, or None if no matching case was found or the update failed
        """
        field_map = field_map if field_map is not None else DEFAULT_FIELD_MAP
        if not content:
            self.___logger.debug("No content to update for %s, skipped", automation_id)
            return None
        case_id = self.__get_all_auto_cases().get(automation_id)
        if not case_id:
            self.___logger.debug("No matching TestRail case found for %s, skipped", automation_id)
            return None
        payload = self.__map_fields(content, field_map)
        try:
            case = self.__api.cases.update_case(case_id, **payload)
        except Exception as error:  # pylint: disable=broad-except
            self.___logger.error("Update case %s failed.\nError%s", case_id, format_error(error))
            return None
        self.___logger.debug("Updated TestRail case %s (%s)", case_id, automation_id)
        return case

    def process_file(self, file_path: str, extra_context=None, field_map=None, dry_run=False) -> list:
        """
        Extract tests from a file, generate content for each and update the matching TestRail cases

        :param file_path: path to the python test file, string
        :param extra_context: extra free-form context to add to the prompt, string, optional
        :param field_map: mapping of content key -> TestRail field name, dict, optional
        :param dry_run: if True, content is generated but TestRail is not updated, bool
        :return: list of dicts with keys: automation_id, content, case (None if not updated)
        """
        results = []
        for test in self.extract_tests_from_file(file_path):
            content = self.generate_content(test, extra_context=extra_context)
            case = None if dry_run else self.update_testrail_case(test["automation_id"], content, field_map=field_map)
            results.append({"automation_id": test["automation_id"], "content": content, "case": case})
        return results

    def process_files(self, file_paths: list, extra_context=None, field_map=None, dry_run=False) -> list:
        """
        Run process_file for a list of files

        :param file_paths: list of paths to python test files, list of strings
        :param extra_context: extra free-form context to add to the prompt, string, optional
        :param field_map: mapping of content key -> TestRail field name, dict, optional
        :param dry_run: if True, content is generated but TestRail is not updated, bool
        :return: list of dicts with keys: automation_id, content, case (None if not updated)
        """
        results = []
        for file_path in file_paths:
            results.extend(
                self.process_file(file_path, extra_context=extra_context, field_map=field_map, dry_run=dry_run)
            )
        return results
