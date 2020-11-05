import unittest
from tclib import library
from libpipeline.settings import Settings
from libpipeline.events.base import Event
from libpipeline.workflows.factory import WorkflowFactory
from libpipeline.workflows.isolated import IsolatedWorkflow, GroupedWorkflow
from libpipeline.workflows.builtin import UnknownWorkflow, ManualWorkflow
from libpipeline.testruns import CaseRunConfiguration, CaseRunConfigurationsList, TestRuns
from libpipeline.result import Result


class TestWorkflowIsolated(IsolatedWorkflow):
    def execute(self):
        pass

    def terminate(self):
        return False

    def displayStatus(self):
        return 'Test'


class TestWorkflowGroupedAll(GroupedWorkflow):
    def execute(self):
        pass

    def groupTerminate(self):
        return False

    def groupDisplayStatus(self):
        return 'Test'

    @classmethod
    def factory(cls, testRuns, crcIds):
        cls(testRuns, crcIds)


class TestWorkflowGrouped(GroupedWorkflow):
    def execute(self):
        pass

    def groupTerminate(self):
        return False

    def groupDisplayStatus(self):
        return 'Test'

    @classmethod
    def factory(cls, testRuns, crcList):
        # Split caseruns into groups by architecture
        for crcList in crcList.by_configuration('arch').values():
            cls(testRuns, crcList)


def testruns_init():
        lib = library.Library('tests/test_library')
        settings = Settings(cmdline_overrides={'library': {'defaultCaseConfigMergeMethod': 'extension'}}, environment={}, settings_locations=[])
        event = Event('test', {}, ['test_workflows'])
        return TestRuns(lib, event, settings)


class TestAssignWorkflows1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        WorkflowFactory.clear_workflow_classes()
        WorkflowFactory.register('test_isolated')(TestWorkflowIsolated)
        WorkflowFactory.register('test_grouped')(TestWorkflowGroupedAll)
        cls.testruns = testruns_init()

    @classmethod
    def tearDownClass(cls):
        WorkflowFactory.restore_workflow_classes()

    def test_isolated(self):
        for caserun in self.testruns.caseRunConfigurations:
            if caserun.testcase.name == 'test_isolated 1':
                workflow1 = caserun.workflow
            if caserun.testcase.name == 'test_isolated 2':
                workflow2 = caserun.workflow

        self.assertIsInstance(workflow1, TestWorkflowIsolated)
        self.assertIsInstance(workflow2, TestWorkflowIsolated)
        self.assertNotEqual(workflow1, workflow2)

    def test_grouped_all(self):
        for caserun in self.testruns.caseRunConfigurations:
            if caserun.testcase.name == 'test_grouped 1':
                workflow1 = caserun.workflow
            if caserun.testcase.name == 'test_grouped 2':
                workflow2 = caserun.workflow
            if caserun.testcase.name == 'test_grouped 3':
                workflow3 = caserun.workflow

        self.assertIsInstance(workflow1, TestWorkflowGroupedAll)
        self.assertIsInstance(workflow2, TestWorkflowGroupedAll)
        self.assertIsInstance(workflow3, TestWorkflowGroupedAll)
        self.assertEqual(workflow1, workflow2)
        self.assertEqual(workflow2, workflow3)

    def test_manual(self):
        for caserun in self.testruns.caseRunConfigurations:
            if caserun.testcase.name == 'testcase 1':
                workflow = caserun.workflow

        self.assertIsInstance(workflow, ManualWorkflow)

    def test_unknown(self):
        for caserun in self.testruns.caseRunConfigurations:
            if caserun.testcase.name == 'testcase 2':
                workflow = caserun.workflow

        self.assertIsInstance(workflow, UnknownWorkflow)


class TestAssignWorkflows2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        WorkflowFactory.clear_workflow_classes()
        WorkflowFactory.register('test_grouped')(TestWorkflowGrouped)
        cls.testruns = testruns_init()

    @classmethod
    def tearDownClass(cls):
        WorkflowFactory.restore_workflow_classes()

    def test_grouped_by_config(self):
        for caserun in self.testruns.caseRunConfigurations:
            if caserun.testcase.name == 'test_grouped 1':
                workflow1 = caserun.workflow
            if caserun.testcase.name == 'test_grouped 2':
                workflow2 = caserun.workflow
            if caserun.testcase.name == 'test_grouped 3':
                workflow3 = caserun.workflow

        self.assertIsInstance(workflow1, TestWorkflowGrouped)
        self.assertIsInstance(workflow2, TestWorkflowGrouped)
        self.assertIsInstance(workflow3, TestWorkflowGrouped)
        self.assertEqual(workflow1, workflow2)
        self.assertNotEqual(workflow2, workflow3)


class DummyTestCase():
    def __init__(self, name):
        self.name = name
        self.execution = unittest.mock.MagicMock()
        self.execution.type = 'test'
        self.id = name

class DummyTestPlan():
    def __init__(self, name):
        self.name = name
        self.id = name

class TestCaseRunConfigurationsList(unittest.TestCase):
    def setUp(self):
        planA = DummyTestPlan('A')
        planB = DummyTestPlan('B')

        self.crc11 = CaseRunConfiguration(DummyTestCase('testcase1'), {'conf': 1, 'a': 0}, [planA])
        self.crc11.result = Result('running', 'PASS', False)

        self.crc12 = CaseRunConfiguration(DummyTestCase('testcase1'), {'conf': 2, 'a': 0}, [planA, planB])
        self.crc12.result = Result('complete', 'FAIL', False)

        self.crc21 = CaseRunConfiguration(DummyTestCase('testcase2'), {'conf': 1, 'a': 1}, [planB])
        self.crc21.result = Result('DNF', None, False)

        self.crc23 = CaseRunConfiguration(DummyTestCase('testcase2'), {'conf': 3, 'a': 1}, [planB])
        self.crc23.result = Result('DNF', 'ERROR', False)

        self.crcList = CaseRunConfigurationsList([
            self.crc11, self.crc12,
            self.crc21, self.crc23,
        ])

    def test_append(self):
        caserun_configurations = CaseRunConfigurationsList()
        caserun_configurations.append(1)
        self.assertListEqual(caserun_configurations, [1])
        caserun_configurations.append(1)
        self.assertListEqual(caserun_configurations, [2])
        caserun_configurations.append(3)
        self.assertListEqual(caserun_configurations, [2, 3])

    def test_by_testcase(self):
        self.assertEqual(
            self.crcList.by_testcase(),
            {
                'testcase1' : CaseRunConfigurationsList([self.crc11, self.crc12]),
                'testcase2' : CaseRunConfigurationsList([self.crc21, self.crc23]),
            },
        )

    def test_by_workflowType(self):
        self.assertEqual(
            self.crcList.by_workflowType(),
            {
                'test' : self.crcList,
            },
        )

    def test_by_configuration(self):
        self.assertEqual(
            self.crcList.by_configuration('conf'),
            {
                (1,) : CaseRunConfigurationsList([self.crc11, self.crc21]),
                (2,) : CaseRunConfigurationsList([self.crc12]),
                (3,) : CaseRunConfigurationsList([self.crc23]),
            },
        )
        self.assertEqual(
            self.crcList.by_configuration('a'),
            {
                (0,) : CaseRunConfigurationsList([self.crc11, self.crc12]),
                (1,) : CaseRunConfigurationsList([self.crc21, self.crc23]),
            },
        )
        self.assertEqual(
            self.crcList.by_configuration('conf', 'a'),
            {
                (1,0) : CaseRunConfigurationsList([self.crc11]),
                (2,0) : CaseRunConfigurationsList([self.crc12]),
                (1,1) : CaseRunConfigurationsList([self.crc21]),
                (3,1) : CaseRunConfigurationsList([self.crc23]),
            },
        )

    def test_by_testplan(self):
        self.assertEqual(
            self.crcList.by_testplan(),
            {
                'A' : CaseRunConfigurationsList([self.crc11, self.crc12]),
                'B' : CaseRunConfigurationsList([self.crc12, self.crc21, self.crc23]),
            },
        )

    def test_combined(self):
        self.assertEqual(
            {
                testplan : crcList.by_testcase()
                for testplan, crcList
                in self.crcList.by_testplan().items()
            },
            {
                'A' : {
                    'testcase1' : CaseRunConfigurationsList([self.crc11, self.crc12]),
                },
                'B' : {
                    'testcase1' : CaseRunConfigurationsList([self.crc12]),
                    'testcase2' : CaseRunConfigurationsList([self.crc21, self.crc23]),
                },
            },
        )

    def test_result(self):
        self.assertEqual(self.crcList.status, 'running')
        self.assertEqual(
            {
                testcase: crcList.result
                for testcase, crcList
                in self.crcList.by_testcase().items()
            },
            {
                'testcase1' : 'FAIL',
                'testcase2' : 'ERROR',
            }
        )

    def test_status(self):
        self.assertEqual(self.crcList.result, 'ERROR')
        self.assertEqual(
            {
                testcase: crcList.status
                for testcase, crcList
                in self.crcList.by_testcase().items()
            },
            {
                'testcase1' : 'running',
                'testcase2' : 'DNF',
            }
        )
