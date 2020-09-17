import threading
import queue
import abc
import logging

from ..testruns.result import Result
from ..exceptions import UnexpectedState

LOGGER = logging.getLogger(__name__)

class BaseReportSender(threading.Thread, metaclass=abc.ABCMeta):
    """
    Base class for case-run-configuration report sender.

    The ReportSender classes are responsible for handling results according
    to the specification provided in the testplan in reporting structure.

    The ReportSender has associated case-run-configurations and reacts on the
    execution progress which is represented by provided Result instances. Based
    on the content of reporting structure and settings, each class should
    deliver the desired reporting.

    :param testplan: TestPlan instance for which the reporting should be done.
    :type testplan: tclib.structures.testplan.TestPlan
    :param reporting_structure: Test Plan reporting item containing data for this instance.
    :type reporting_structure: tclib.structures.testplan.Reporting
    :param caseRunConfigurations: List of case-run-configurations for which the reports should be sent.
    :type caseRunConfigurations: list[:class:`libpipeline.testrun.CaseRunConfiguration`]
    :param event: Event based on which the reporting should be done. The ReportSender may use this to obtain more information useful for reporting.
    :type event: libpipeline.events.base.Event
    :param settings: Pipeline settings object
    :type settings: libpipeline.settings.Settings
    """
    def __init__(self, testplan, reporting_structure, caseRunConfigurations, event, settings):
        super().__init__()
        self.testplan = testplan
        self.reporting = reporting_structure
        self.caseRunConfigurations = caseRunConfigurations
        self.event = event
        self.settings = settings
        self.resultsQueue = queue.Queue()

    def run(self):
        LOGGER.debug("ReportSender started: '%s'", self)
        self.processTestRunStarted()
        while True:
            item = self.resultsQueue.get()
            LOGGER.debug("'%s' processing: '%s'", self, item)
            if isinstance(item, Result):
                if self.processResult(item):
                    self.resultsQueue.task_done()
                    break
                self.resultsQueue.task_done()
            # TODO: catch finished test case here
            # TODO: catch end of test run here
        LOGGER.debug("'%s' finished processing items (test run should be complete)", self)
        self.processTestRunFinished()
        self.checkEmptyQueue()

    def resultUpdate(self, result):
        """
        Notify ReportSender about new result. This method is meant to be used
        from outside of the ReportSender and should not contain processing
        of the result itself.

        Default implementation just puts the result to a queue which is later
        processed by the ReportSender in its thread.
        """
        self.resultsQueue.put(result)

    def processResult(self, result):
        """
        This method is called in the loop processing results queue and signals
        if the result was the last one and reportsender should end.

        :param result: Result to be processed.
        :type result: libpipeline.testrun.result.Result
        :return: True if the processed result is expected to be the last one. False otherwise.
        :rtype: bool
        """
        if result.final:
            self.processFinalResult(result)
            return True
        self.processPartialResult(result)
        return False

    def checkEmptyQueue(self):
        """
        :raises UnexpectedState: when the results queue is not empty.
        :return: None
        :rtype: None
        """
        if not self.resultsQueue.empty():
            raise UnexpectedState("The reportSender queue isn't empty.")

    @abc.abstractmethod
    def processPartialResult(self, result):
        """
        This method is called when a caseRunResult updates it's state or result.

        Example of use for this method: Send in-progress notifications.

        :param result: Result object holding information about the new state.
        :type result: ..testruns.Result
        """
        pass

    @abc.abstractmethod
    def processFinalResult(self, result):
        """
        This method is called when a caseRunResult performs final change of
        state or result.

        Example of use for this method: Send finished case-run-configuration notification or upload its result.

        :param result: Result object holding information about the new state.
        :type result: ..testruns.Result
        """
        pass

    @abc.abstractmethod
    def processTestRunStarted(self):
        """
        This method is called when TestRun (handled by this ResultsSender
        instance) is started.

        Example of use for this method: create TestRun in test
        case management system.
        """
        pass

    @abc.abstractmethod
    def processTestRunFinished(self):
        """
        This method is called when TestRun (handled by this ResultsSerder
        instance) is finished (meaning that all worklows associated to the
        case-run-configurations are no longer running).

        Examples of use for this method:

         * Mark TestRun in test case management system as finished if there are
           no manual (or aborted/canceled) case-run-configurations.
         * Send email with results summary.
        """
        pass

    @abc.abstractmethod
    def processCaseRunFinished(self, testCaseID):
        """
        This method is called when all case-run-configurations of the TestCase
        associated with the TestRun (handled by this ResultsSender instance)
        have final result associated.
        """
        pass
