import unittest

from ..testruns.result import Result
from .factory import WorkflowFactory
from .builtin import UnknownWorkflow, ManualWorkflow

class FakeCaseRunConfiguration():
    def __init__(self):
        self.workflow = None
        self.results = []

    def updateResult(self, result):
        resultcopy = result.copy()
        resultcopy.caseRunConfiguration = self
        self.results.append(resultcopy)

class TestWorkflowsRegistered(unittest.TestCase):
    def test_manual(self):
        self.assertEqual(WorkflowFactory.workflow_classes['manual'], ManualWorkflow)

    def test_unknown(self):
        self.assertEqual(WorkflowFactory.workflow_classes[None], UnknownWorkflow)

class TestManual(unittest.TestCase):
    def test_run(self):
        caseRunConfiguration = FakeCaseRunConfiguration()
        workflow = ManualWorkflow(caseRunConfiguration, None, None)
        workflow.start()
        workflow.join()
        self.assertEqual(
            caseRunConfiguration.results,
            [Result('DNF', None, True, caseRunConfiguration)]
        )

class TestUnknown(unittest.TestCase):
    def test_run(self):
        caseRunConfiguration = FakeCaseRunConfiguration()
        workflow = UnknownWorkflow(caseRunConfiguration, None, None)
        workflow.start()
        workflow.join()
        self.assertEqual(
            caseRunConfiguration.results,
            [Result('DNF', 'ERROR', True, caseRunConfiguration)]
        )
