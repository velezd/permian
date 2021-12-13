import unittest
from libpermian.settings import Settings
from libpermian.workflows.factory import WorkflowFactory
from libpermian.workflows.isolated import IsolatedWorkflow
from libpermian.workflows.builtin import UnknownWorkflow
from libpermian.caserunconfiguration import CaseRunConfiguration, CaseRunConfigurationsList

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

    @unittest.mock.patch('libpermian.testruns.TestRuns', autospec=True)
    def test_unknown(self, MockTestRuns):
        caseRunConfiguration = CaseRunConfiguration(DummyTestCase(), {}, [])
        testRuns = MockTestRuns(None, None, None)
        testRuns.caseRunConfigurations = CaseRunConfigurationsList(
            [caseRunConfiguration]
        )
        testRuns.__getitem__ = lambda instance, key: caseRunConfiguration if key == caseRunConfiguration.id else None
        testRuns.event = None
        testRuns.settings = Settings({}, {}, [])
        WorkflowFactory._assignWorkflows('unknown', testRuns, testRuns.caseRunConfigurations)
        self.assertIsInstance(caseRunConfiguration.workflow, UnknownWorkflow)
