# TestRail reporter
This is Testrail API reporter tools.

This package contains several tools to interact with TestRail via API.

General part is *TestRailResultsReporter* which is designed to report test results via api. This part is close to trcli, but without nasty bugs.

Firstly, you need to obtain test results in xml format. You can do it via running your testsuite, i.e. using pytest:

```
pytest --junitxml "junit-report.xml" "./tests"
```

Also you need to add custom field (string type) to TestRails with name `automation_id`.

Now, you ready to upload results to TestRails.
To it, use:

```
url=https://your_tr.testrail.io`
email=your@email.com
password=your_password
project_number=42
test_suite_number=66
api=TestRailResultsReporter(url=url, email=email, password=password, project_id=project_id, suite_id=test_suite_id)
# then just call:
api.send_results()
```
After this new testcases, test run and test results will be created. Testrun will have a name like `AT run 2022-09-01T20:25:51`

If you fill `automation_id` for existing testcases using correct format `path.to.testfile.filename.test_class.test_step`, then in such case results will be added to existing testcases.

Also, you can customize test run by passing:
- `title` param to send_results function - it will replace whole test run title.
- `environment` - it will be added to end of string like `AT run 2022-09-01T20:25:51 on Dev`
- `timestamp` - it will replace timestamp, obtained from XML file)
- `run_id` - if specified, results will be added to test run, no new testrun will be created
- `close_run` - may be `True` (by default) or `False` - if `True`, then eery testrun will be closed.

Also, you can setup other params separately without need to re-initialize api object:

```set_project_id(project_id)``` - change project id
```def set_suite_id(suite_id)``` - change suite id
```def set_xml_filename(xml_filename):``` - change path/filename of xml report
```set_at_report_section(section_name)``` - change default folder name where non-linked testcases will be created
```set_timestamp(new_timestamp)``` - change default timestamp to custom
