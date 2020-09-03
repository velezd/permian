import threading
import queue
import abc
import logging

from ..testruns.result import Result
from ..exceptions import UnexpectedState

LOGGER = logging.getLogger(__name__)

class BaseReportSender(threading.Thread, metaclass=abc.ABCMeta):
    """
    Base class for case-run-configuration results sender.

    :param reporting_structure: The whole Test Plan reporting item associated with this ReportSender.
    :type reporting_structure: tclib.DataObject
    :param settings: Pipeline settings object
    :type settings: TODO
    """
    def __init__(self, reporting_structure, caseRunConfigurations, settings):
        super().__init__(self)
        self.reporting = reporting_structure
        self.caseRunConfigurations = caseRunConfigurations
        self.settings = settings
        self.processQueue = queue.Queue()

    def run(self):
        LOGGER.debug("ReportSender started: '%s'", self)
        self.processTestRunStarted()
        while True:
            item = self.processQueue.get()
            LOGGER.debug("'%s' processing: '%s'", self, item)
            if isinstance(item, Result):
                if self.processResult(item):
                    self.processQueue.task_done()
                    break
                self.processQueue.task_done()
            # TODO: catch finished test case here
            # TODO: catch end of test run here
            self.processQueue.task_done()
        LOGGER.debug("'%s' finished processing items (test run should be complete)", self)
        self.processTestRunFinished()
        self.checkEmptyQueue()

    def processResult(self, result):
        if result.final:
            self.processFinalResult(result)
            return True
        self.processPartialResult(result)
        return False

    def checkEmptyQueue(self):
        if not self.processQueue.empty():
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
