import unittest

from ..settings import Settings
from ..testruns import TestRuns
from ..result import Result
from .factory import WorkflowFactory
from .builtin import UnknownWorkflow, ManualWorkflow

class FakeCaseRunConfiguration():
    def __init__(self):
        self.workflow = None
        self.id = 'someId'

class TestWorkflowsRegistered(unittest.TestCase):
    def test_manual(self):
        self.assertEqual(WorkflowFactory.workflow_classes['manual'], ManualWorkflow)

    def test_unknown(self):
        self.assertEqual(WorkflowFactory.workflow_classes[None], UnknownWorkflow)

class TestManual(unittest.TestCase):
    def test_run(self):
        caseRunConfiguration = FakeCaseRunConfiguration()
        testRuns = unittest.mock.create_autospec(TestRuns)(None, None, None)
        testRuns.caseRunConfigurations = [caseRunConfiguration]
        testRuns.event = None
        testRuns.settings = Settings({}, {}, [])
        workflow = ManualWorkflow(testRuns, caseRunConfiguration.id)
        workflow.start()
        workflow.join()
        testRuns.updateResult.assert_called_once_with(caseRunConfiguration.id, Result('DNF', None, True))

class TestUnknown(unittest.TestCase):
    def test_run(self):
        caseRunConfiguration = FakeCaseRunConfiguration()
        testRuns = unittest.mock.create_autospec(TestRuns)(None, None, None)
        testRuns.caseRunConfigurations = [caseRunConfiguration]
        testRuns.event = None
        testRuns.settings = Settings({}, {}, [])
        workflow = UnknownWorkflow(testRuns, caseRunConfiguration.id)
        workflow.start()
        workflow.join()
        testRuns.updateResult.assert_called_once_with(caseRunConfiguration.id, Result('DNF', 'ERROR', True))
