import unittest

from ..testruns.result import Result
from .factory import WorkflowFactory
from .builtin import UnknownWorkflow, ManualWorkflow

class FakeCaseRunConfiguration():
    def __init__(self):
        self.workflow = None
        self.results = []

    def updateResult(self, result):
        self.results.append(result)

class TestWorkflowsRegistered(unittest.TestCase):
    def test_manual(self):
        self.assertEqual(WorkflowFactory.workflow_classes['manual'], ManualWorkflow)

    def test_unknown(self):
        self.assertEqual(WorkflowFactory.workflow_classes[None], UnknownWorkflow)

class TestManual(unittest.TestCase):
    def test_run(self):
        caseRunConfiguration = FakeCaseRunConfiguration()
        workflow = ManualWorkflow(caseRunConfiguration)
        workflow.start()
        workflow.join()
        self.assertEqual(
            caseRunConfiguration.results,
            [Result(caseRunConfiguration, 'DNF', None, True)]
        )

class TestUnknown(unittest.TestCase):
    def test_run(self):
        caseRunConfiguration = FakeCaseRunConfiguration()
        workflow = UnknownWorkflow(caseRunConfiguration)
        workflow.start()
        workflow.join()
        self.assertEqual(
            caseRunConfiguration.results,
            [Result(caseRunConfiguration, 'DNF', 'ERROR', True)]
        )
