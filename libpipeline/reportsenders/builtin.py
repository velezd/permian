import logging

from .base import BaseReportSender
from .factory import ReportSenderFactory

LOGGER = logging.getLogger(__name__)

@ReportSenderFactory.register(None)
class UnknownReportSender(BaseReportSender):
    def __init__(self, testplan, reporting_structure, *args, **kwargs):
        super().__init__(testplan, reporting_structure, *args, **kwargs)
        LOGGER.error(
            'No reportSender was found for "%s". Falling back to UnknownReportSender, fix this please.', reporting_structure.type
        )

    def processPartialResult(self, result):
        LOGGER.info('%s reporting partial result: %s', self, result)

    def processFinalResult(self, result):
        LOGGER.info('%s reporting final result %s', self, result)

    def processTestRunStarted(self):
        LOGGER.info('%s reporting Test Run started', self)

    def processTestRunFinished(self):
        LOGGER.info('%s reporting Test Run finished', self)

    def processCaseRunFinished(self, testCaseID):
        LOGGER.info('%s reporting Case Run of "%s" finished', self, testCaseID)
