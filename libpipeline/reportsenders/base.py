import threading
import queue
import abc
import logging

from ..caserunconfiguration import CaseRunConfiguration, CaseRunConfigurationsList
from ..exceptions import UnexpectedState
from ..exception_dump import dump_exception


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
    description_format = "Configuration: %s - Result: %s, %s - Links: %s ; "
    def __init__(self, testplan, reporting_structure, caseRunConfigurations, event, settings, issueAnalyzerProxy, group=None):
        super().__init__()
        self.testplan = testplan
        self.reporting = reporting_structure
        # Create local copy of caseRunConfiguration, to prevent unwanted interaction between different ReportSenders
        self.caseRunConfigurations = caseRunConfigurations
        self.event = event
        self.settings = settings
        self.dry_run = self.settings.getboolean('reportSenders', 'dry_run')
        self.issueAnalyzerProxy = issueAnalyzerProxy
        self.group=group
        self.resultsQueue = queue.Queue()
        self.exception = None

    def setUp(self):
        """ Executed just before the ReportSender starts """
        pass

    def tearDown(self):
        """ Executed after the ReportSender has finished """
        pass

    def run(self):
        LOGGER.debug("ReportSender started: '%s'", self)
        try:
            self.setUp()
            self.processTestRunStarted()
            while True:
                item = self.resultsQueue.get()
                LOGGER.debug("'%s' processing: '%s'", self, item)
                if isinstance(item, CaseRunConfiguration):
                    if self.processResult(item):
                        self.resultsQueue.task_done()
                        break
                    self.resultsQueue.task_done()
            self.tearDown()
            LOGGER.debug("'%s' finished processing items (test run should be complete)", self)
            self.checkEmptyQueue()
        except Exception as e:
            self.exception = dump_exception(e, self)

    def resultUpdate(self, crc):
        """
        Notify ReportSender about new result. This method is meant to be used
        from outside of the ReportSender and should not contain processing
        of the result itself.

        Default implementation just puts the relevant result to a queue which
        is later processed by the ReportSender in its thread.

        :param result:
        :typer result: libpipeline.testrun.result.Result
        :return: True if the result was relevant to the ReportSender instance. False otherwise.
        :rtype: bool
        """
        if crc not in self.caseRunConfigurations:
            return False
        self.resultsQueue.put(crc)
        return True

    def processResult(self, crcUpdate):
        """
        This method is called in the loop processing results queue and signals
        if the result was the last one and reportsender should end.

        :param result: Result to be processed.
        :type result: libpipeline.testrun.result.Result
        :return: True if the processed result is expected to be the last one. False otherwise.
        :rtype: bool
        """
        localCaseRunConfiguration = self.caseRunConfigurations[crcUpdate.id]
        # Update result of local copy of caseRunConfiguration
        localCaseRunConfiguration.updateResult(crcUpdate.result)
        localCaseRunConfiguration.logs = crcUpdate.logs.copy()

        if crcUpdate.result.final:
            if self.reporting.data is None or self.reporting.data.get('submit_issues', True):
                for issue in self.issuesFor([crcUpdate]):
                    issue.submit()
            self.processFinalResult(crcUpdate)
            # Catch end of test case
            if all([crc.result.final for crc in self.caseRunConfigurations if crcUpdate.testcase == crc.testcase]):
                self.processCaseRunFinished(crcUpdate.testcase.name)
            # Catch end of testun
            if all([crc.result.final for crc in self.caseRunConfigurations]):
                self.processTestRunFinished()
                return True
        else:
            self.processPartialResult(crcUpdate)
        return False

    def checkEmptyQueue(self):
        """
        :raises UnexpectedState: when the results queue is not empty.
        :return: None
        :rtype: None
        """
        if not self.resultsQueue.empty():
            raise UnexpectedState("The reportSender queue isn't empty.")

    def issuesFor(self, crcList):
        """
        Provide issue set for the crcList to find out if the result needs
        additional review or if no review is necessary as all identified issues
        are already known.

        :param crcList: CaseRunConfigurations to be inspected registered issue analyzers
        :type crcList: iterable of CaseRunConfiguration
        :return: Issues found for provided crcList. Check isComplete property to find out if the set of issues is complete. If not, the CaseRunConfiguration results need to be reviewed.
        :rtype: IssueSet
        """
        return self.issueAnalyzerProxy.analyze(crcList)

    def resultOf(self, caseRunConfigurations):
        if not isinstance(caseRunConfigurations, CaseRunConfigurationsList):
            caseRunConfigurations = CaseRunConfigurationsList(caseRunConfigurations)
        result = caseRunConfigurations.result
        issueSet = self.issuesFor(caseRunConfigurations)
        # if there's some issue missing or some issue needs review, use
        # error state as 'needs-review'
        if not issueSet.isComplete or issueSet.needsReview:
            return 'ERROR'
        return caseRunConfigurations.result

    def descriptionOf(self, caseRunConfigurations):
        """
        Provide human readable description of results for provided
        caseRunConfigurations which will be used during reporting

        :param caseRunConfigurations: List of caseRunConfiguration based on which the description should be formed.
        :type caseRunConfigurations: iterable of CaseRunConfiguration
        :return: Human readable description of the results.
        :rtype: str
        """
        descriptions = []
        for crc in caseRunConfigurations:
            descriptions.append(
                self.description_format % (
                    str(crc.configuration),
                    str(crc.result.state),
                    str(crc.result.result),
                    ', '.join([
                        link
                        for link
                        in crc.result.extra_fields.get('beaker_links', ['None'])
                    ]),
                )
            )
        return "".join(descriptions)


    @abc.abstractmethod
    def processPartialResult(self, crc):
        """
        This method is called when a caseRunResult updates it's state or result.

        Example of use for this method: Send in-progress notifications.

        :param result: Result object holding information about the new state.
        :type result: ..testruns.Result
        """
        pass

    @abc.abstractmethod
    def processFinalResult(self, crc):
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
