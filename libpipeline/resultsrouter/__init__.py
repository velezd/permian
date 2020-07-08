from ..reportsenders.factory import ReportSenderFactory

class ResultsRouter():
    """
    This class works as a dispatcher getting information about
    case-run-configuration results changes and sends them (puts into queues)
    to corresponding ResultReporter instances.

    :param testRuns:
    :type testRuns:
    :param library:
    :type library: tclib.library.Library
    """
    def __init__(self, testRuns, library, config):
        for testPlan, caseRunConfigurations in testRuns.testPlansMapping:
            ReportSenderFactory.assign(
                library.testplans[testPlan],
                caseRunConfigurations,
                config,
            )
        self.library = library

    def routeResult(self, result):
        """
        Provide the result to relevant reportSenders for their processing.
        If the result would cause testRun to be complete (meaning all
        caseRunConfigurations belonging to the Test plan have final result)
        notify reportSender about finished test run.
        """
        for testPlan, relevant in result.caseRunConfiguration.running_for.items():
            if relevant:
                for senderInstance in self.library.testplans[testPlan]:
                    senderInstance.queue.put(result)
        # TODO: in case of final result detect if testRun finished and put corresponding object to the queue
