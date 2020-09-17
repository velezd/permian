import unittest
import tclib.library

from ..settings import Settings
from ..events.base import Event
from ..testruns import TestRuns, CaseRunConfiguration
from ..testruns.result import Result
from ..reportsenders.factory import ReportSenderFactory
from ..reportsenders.base import BaseReportSender
from ..reportsenders.builtin import UnknownReportSender
from ..resultsrouter import ResultsRouter

class DummyTestCase():
    name = 'test'

class TestReportSender(BaseReportSender):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.results = []

    def resultUpdate(self, result):
        self.results.append(result)

    def processPartialResult(self, result):
        pass

    def processFinalResult(self, result):
        pass

    def processTestRunStarted(self):
        pass

    def processTestRunFinished(self):
        pass

    def processCaseRunFinished(self, testCaseID):
        pass

class TestResultsRouter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ReportSenderFactory.clear_reportSender_classes()
        ReportSenderFactory.register('test', TestReportSender)

    @classmethod
    def tearDownClass(cls):
        ReportSenderFactory.restore_reportSender_classes()

    def setUp(self):
        self.settings = Settings({}, {}, [])
        self.event = Event('test', {}, ['test1', 'test2'])
        self.library = tclib.library.Library('tests/test_library')
        self.testruns = TestRuns(self.library, self.event, self.settings)

    def tearDown(self):
        pass

    def testAssignment(self):
        resultsRouter = ResultsRouter(self.testruns, self.library, self.event, self.settings)
        result = {
            'testplan 1': (TestReportSender,),
            'testplan 2': (UnknownReportSender,),
        }
        self.assertCountEqual(resultsRouter.reportSenders, result)
        for testplan_id, expected_classes in result.items():
            for i, expected_class in enumerate(expected_classes):
                self.assertIsInstance(
                    resultsRouter.reportSenders[testplan_id][i],
                    expected_class
                )

    def testRouteResultOnePlan(self):
        caseRunConfiguration = CaseRunConfiguration(DummyTestCase(), {}, [self.library.testplans['testplan 1']])
        result = Result('DNF', caseRunConfiguration=caseRunConfiguration)
        resultsRouter = ResultsRouter(self.testruns, self.library, self.event, self.settings)
        resultsRouter.routeResult(result)
        self.assertListEqual([result], resultsRouter.reportSenders['testplan 1'][0].results)
        self.assertTrue(resultsRouter.reportSenders['testplan 2'][0].resultsQueue.empty())

    def testRouteResultMultiplePlans(self):
        caseRunConfiguration = CaseRunConfiguration(DummyTestCase(), {}, [self.library.testplans['testplan 1'], self.library.testplans['testplan 2']])
        result = Result('DNF', caseRunConfiguration=caseRunConfiguration)
        resultsRouter = ResultsRouter(self.testruns, self.library, self.event, self.settings)
        resultsRouter.routeResult(result)
        self.assertListEqual([result], resultsRouter.reportSenders['testplan 1'][0].results)
        self.assertFalse(resultsRouter.reportSenders['testplan 2'][0].resultsQueue.empty())
