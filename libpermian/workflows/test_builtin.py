import unittest

from ..settings import Settings
from ..testruns import TestRuns
from ..caserunconfiguration import CaseRunConfiguration, CaseRunConfigurationsList
from ..result import Result
from .factory import WorkflowFactory
from .builtin import UnknownWorkflow, ManualWorkflow

class DummyTestCase():
    name = 'test'
    id = name

class TestWorkflowsRegistered(unittest.TestCase):
    def test_manual(self):
        self.assertEqual(WorkflowFactory.workflow_classes['manual'], ManualWorkflow)

    def test_unknown(self):
        self.assertEqual(WorkflowFactory.workflow_classes[None], UnknownWorkflow)

def nolog(*args, **kwargs):
    pass

@unittest.mock.patch('libpermian.workflows.grouped.GroupedWorkflow.groupLog', new=nolog)
class TestManual(unittest.TestCase):
    def test_run(self):
        caseRunConfiguration = CaseRunConfiguration(DummyTestCase(), {}, [])
        testRuns = unittest.mock.create_autospec(TestRuns)(None, None, None)
        testRuns.caseRunConfigurations = CaseRunConfigurationsList(
            [caseRunConfiguration]
        )
        testRuns.event = None
        testRuns.settings = Settings({}, {}, [])
        crcExpectedResult = caseRunConfiguration.copy()
        crcExpectedResult.result = Result('DNF', None, True)
        workflow = ManualWorkflow(testRuns, testRuns.caseRunConfigurations)
        workflow.start()
        workflow.join()
        testRuns.update.assert_called_once_with(crcExpectedResult)

@unittest.mock.patch('libpermian.workflows.grouped.GroupedWorkflow.groupLog', new=nolog)
class TestUnknown(unittest.TestCase):
    def test_run(self):
        caseRunConfiguration = CaseRunConfiguration(DummyTestCase(), {}, [])
        testRuns = unittest.mock.create_autospec(TestRuns)(None, None, None)
        testRuns.caseRunConfigurations = CaseRunConfigurationsList(
            [caseRunConfiguration]
        )
        testRuns.event = None
        testRuns.settings = Settings({}, {}, [])
        crcExpectedResult = caseRunConfiguration.copy()
        crcExpectedResult.result = Result('DNF', 'ERROR', True)
        workflow = UnknownWorkflow(testRuns, testRuns.caseRunConfigurations)
        workflow.start()
        workflow.join()
        testRuns.update.assert_called_once_with(crcExpectedResult)
