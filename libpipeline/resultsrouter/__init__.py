from ..reportsenders.factory import ReportSenderFactory

class ResultsRouter():
    """
    This class works as a dispatcher getting information about
    case-run-configuration results changes and sends them (puts into queues)
    to corresponding ResultReporter instances.

    Note: The Event and Settings instances provided doesn't have any influence
    on the routing of the results but the event is passed to ReportSenders
    instances so that they can customize the reporting based on the
    event/settings. They still may have influence on the creation and assignment
    of ReportSender instances to the executed test runs though (under certain
    conditions, some ReportSender instances may not be intentionally created
    and some not defined in the testrun may be additionally created).

    :param testRuns: TestRuns for which the results should be routed.
    :type testRuns: libpipeline.testruns.TestRuns
    :param library: Library containing definitions of testplans based on which the reporting is constructed.
    :type library: tclib.library.Library
    :param event: Event for which the reporting should be happening.
    :type event: libpipeline.events.base.BaseEvent
    :param settings: Settings instance which is provided to ReportSenders.
    :type settings: libpipeline.settings.Settings
    """
    def __init__(self, testRuns, library, event, settings):
        self.reportSenders = {}
        for testPlanId, caseRunConfigurations in testRuns.testPlansMapping.items():
            self.reportSenders[testPlanId] = tuple(ReportSenderFactory.assign(
                library.testplans[testPlanId],
                caseRunConfigurations,
                event,
                settings,
            ))
        self.library = library
        self.event = event
        self.settings = settings

    def routeResult(self, result):
        """
        Provide the result to relevant reportSenders for their processing.
        If the result would cause testRun to be complete (meaning all
        caseRunConfigurations belonging to the Test plan have final result)
        notify reportSender about finished test run.
        """
        for testPlan, relevant in result.caseRunConfiguration.running_for.items():
            if relevant:
                for senderInstance in self.reportSenders[testPlan]:
                    senderInstance.resultUpdate(result)
        # TODO: in case of final result detect if testRun finished and put corresponding object to the queue

    def start(self):
        for senderInstances in self.reportSenders.values():
            for senderInstance in senderInstances:
                senderInstance.start()

    def wait(self):
        for senderInstances in self.reportSenders.values():
            for senderInstance in senderInstances:
                senderInstance.join()
