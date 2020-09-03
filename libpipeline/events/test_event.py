import unittest
from unittest.mock import patch
from .base import Event
from ..settings import Settings
from tclib import library


class TestCaseRunsConfigurationsMerge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.library = library.Library('tests/test_library')
        cls.event = Event('test', {}, ['test1'])

    def test_merge_extend(self):
        settings = Settings(cmdline_overrides={'library': {'defaultCaseConfigMergeMethod': 'extension'}}, environment={}, settings_locations=[])
        self.library.testplans['testplan 1'].configurations = [{'arch': 'x86_64', 'variant': 'BaseOS'},
                                                               {'arch': 'x86_64', 'variant': 'AppStream'},
                                                               {'arch': 'ppc64le'}]
        self.library.testcases['testcase 1'].configurations = [{'arch': 'x86_64'},
                                                               {'arch': 'x86_64', 'variant': 'CaseOnly'}]

        result = [{'arch': 'x86_64', 'variant': 'AppStream'},
                  {'arch': 'x86_64', 'variant': 'BaseOS'}]

        caserun_configurations = [ caserun.configuration for caserun in self.event.generate_caseRunConfigurations(self.library, settings) ]
        self.assertCountEqual(caserun_configurations, result)

    def test_merge_intersection(self):
        settings = Settings(cmdline_overrides={'library': {'defaultCaseConfigMergeMethod': 'intersection'}}, environment={}, settings_locations=[])
        self.library.testplans['testplan 1'].configurations = [{'arch': 'x86_64', 'variant': 'BaseOS'},
                                                               {'arch': 'x86_64', 'variant': 'AppStream'},
                                                               {'arch': 'ppc64le'}]
        self.library.testcases['testcase 1'].configurations = [{'arch': 'x86_64'},
                                                               {'arch': 'x86_64', 'variant': 'AppStream'},
                                                               {'variant': 'BaseOS'}]

        result = [{'arch': 'x86_64', 'variant': 'AppStream'}]

        caserun_configurations = [ caserun.configuration for caserun in self.event.generate_caseRunConfigurations(self.library, settings) ]
        self.assertCountEqual(caserun_configurations, result)

    def test_merge_empty_plan(self):
        settings = Settings(cmdline_overrides={'library': {'defaultCaseConfigMergeMethod': 'extension'}}, environment={}, settings_locations=[])
        self.library.testplans['testplan 1'].configurations = None
        self.library.testcases['testcase 1'].configurations = [{'arch': 'x86_64'},
                                                               {'arch': 'x86_64', 'variant': 'AppStream'},
                                                               {'variant': 'BaseOS'}]

        result = self.library.testcases['testcase 1'].configurations
        caserun_configurations = [ caserun.configuration for caserun in self.event.generate_caseRunConfigurations(self.library, settings) ]
        self.assertCountEqual(caserun_configurations, result)

    def test_merge_empty_case(self):
        settings = Settings(cmdline_overrides={'library': {'defaultCaseConfigMergeMethod': 'extension'}}, environment={}, settings_locations=[])
        self.library.testplans['testplan 1'].configurations = [{'arch': 'x86_64', 'variant': 'BaseOS'},
                                                               {'arch': 'x86_64', 'variant': 'AppStream'},
                                                               {'arch': 'ppc64le'}]
        self.library.testcases['testcase 1'].configurations = None

        result = self.library.testplans['testplan 1'].configurations
        caserun_configurations = [ caserun.configuration for caserun in self.event.generate_caseRunConfigurations(self.library, settings) ]
        self.assertCountEqual(caserun_configurations, result)

    def test_merge_no_config(self):
        settings = Settings(cmdline_overrides={'library': {'defaultCaseConfigMergeMethod': 'extension'}}, environment={}, settings_locations=[])
        self.library.testplans['testplan 1'].configurations = None
        self.library.testcases['testcase 1'].configurations = None

        result = [{}]
        caserun_configurations = [ caserun.configuration for caserun in self.event.generate_caseRunConfigurations(self.library, settings) ]
        self.assertCountEqual(caserun_configurations, result)

class TestCaseRunsRunningFor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.library = library.Library('tests/test_library')
        cls.settings = Settings(cmdline_overrides={'library': {'defaultCaseConfigMergeMethod': 'extension'}}, environment={}, settings_locations=[])
        cls.event = Event('test', {}, ['test1', 'test2'])

    def test_single_caserun(self):
        self.library.testplans['testplan 1'].configurations = None
        self.library.testplans['testplan 2'].configurations = None

        result = [{'testplan 1': True, 'testplan 2': True}]
        caseruns = [ caserun.running_for for caserun in self.event.generate_caseRunConfigurations(self.library, self.settings) ]
        self.assertCountEqual(caseruns, result)

    def test_multiple_caseruns(self):
        self.library.testplans['testplan 1'].configurations = [{'arch': 'x86_64'}]
        self.library.testplans['testplan 2'].configurations = None

        result = [{'testplan 1': True}, {'testplan 2': True}]
        caseruns = [ caserun.running_for for caserun in self.event.generate_caseRunConfigurations(self.library, self.settings) ]
        self.assertCountEqual(caseruns, result)
