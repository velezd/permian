import unittest
from . import CaseRunConfigurationsList


class TestCaseRunConfigurationsList(unittest.TestCase):
    def test_caserun_configurations_list(self):
        caserun_configurations = CaseRunConfigurationsList()
        caserun_configurations.append(1)
        self.assertListEqual(caserun_configurations, [1])
        caserun_configurations.append(1)
        self.assertListEqual(caserun_configurations, [2])
        caserun_configurations.append(3)
        self.assertListEqual(caserun_configurations, [2, 3])
