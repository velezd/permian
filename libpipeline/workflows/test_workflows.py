import unittest
from libpipeline.workflows.factory import WorkflowFactory
from libpipeline.workflows.isolated import IsolatedWorkflow
from libpipeline.workflows.builtin import UnknownWorkflow
from libpipeline.testruns import CaseRunConfiguration

class TestWorkflow(IsolatedWorkflow):
    def execute(self):
        pass

    def terminate(self):
        return False

    def displayStatus(self):
        return 'Test'

class TestWorkflowFactory(unittest.TestCase):
    old_workflow_classes = []

    @classmethod
    def setUpClass(cls):
        cls.old_workflow_classes = WorkflowFactory.workflow_classes.copy()
        WorkflowFactory.register('test')(TestWorkflow)

    @classmethod
    def tearDownClass(cls):
        WorkflowFactory.workflow_classes = cls.old_workflow_classes

    def test_registered(self):
        self.assertIs(TestWorkflow, WorkflowFactory.workflow_classes['test'])

    def test_unknown(self):
        caserunconf = CaseRunConfiguration('test', {}, [])
        WorkflowFactory._assignWorkflows('unknown', [caserunconf])
        self.assertIsInstance(caserunconf.workflow, UnknownWorkflow)
