import unittest
from libpipeline.workflows.factory import WorkflowFactory
from libpipeline.workflows.isolated import IsolatedWorkflow
from libpipeline.workflows.builtin import UnknownWorkflow
from libpipeline.testruns import CaseRunConfiguration

class DummyTestCase():
    name = 'test'

class TestWorkflow(IsolatedWorkflow):
    def execute(self):
        pass

    def terminate(self):
        return False

    def displayStatus(self):
        return 'Test'

class TestWorkflowFactory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        WorkflowFactory.clear_workflow_classes()
        WorkflowFactory.register('test')(TestWorkflow)

    @classmethod
    def tearDownClass(cls):
        WorkflowFactory.restore_workflow_classes()

    def test_registered(self):
        self.assertIs(TestWorkflow, WorkflowFactory.workflow_classes['test'])

    def test_unknown(self):
        caserunconf = CaseRunConfiguration(DummyTestCase(), {}, [])
        WorkflowFactory._assignWorkflows('unknown', [caserunconf], None, None)
        self.assertIsInstance(caserunconf.workflow, UnknownWorkflow)
