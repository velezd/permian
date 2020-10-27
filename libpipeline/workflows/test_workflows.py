import unittest
from libpipeline.settings import Settings
from libpipeline.workflows.factory import WorkflowFactory
from libpipeline.workflows.isolated import IsolatedWorkflow
from libpipeline.workflows.builtin import UnknownWorkflow
from libpipeline.testruns import CaseRunConfiguration

class DummyTestCase():
    name = 'test'
    id = name

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

    @unittest.mock.patch('libpipeline.testruns.TestRuns', autospec=True)
    def test_unknown(self, MockTestRuns):
        caseRunConfiguration = CaseRunConfiguration(DummyTestCase(), {}, [])
        testRuns = MockTestRuns(None, None, None)
        testRuns.caseRunConfigurations = [caseRunConfiguration]
        testRuns.__getitem__ = lambda instance, key: caseRunConfiguration if key == caseRunConfiguration.id else None
        testRuns.event = None
        testRuns.settings = Settings({}, {}, [])
        WorkflowFactory._assignWorkflows('unknown', testRuns, [caseRunConfiguration.id])
        self.assertIsInstance(caseRunConfiguration.workflow, UnknownWorkflow)
