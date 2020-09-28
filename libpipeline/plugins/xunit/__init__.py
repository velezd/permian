from .xunit import BaseXunitReportSender
from .. import api
from os import path
import re


@api.reportsenders.register('xunit')
class XunitReportSender(BaseXunitReportSender):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.xunit_filename = 'xunit-%s.xml' % re.sub(r'/', '_', self.testplan.name)

    def processPartialResult(self, result):
        pass

    def processFinalResult(self, result):
        pass

    def processTestRunStarted(self):
        pass

    def processTestRunFinished(self):
        with open(path.join(self.settings.get('reportSenders', 'reporting_dir'), self.xunit_filename), 'w') as xunit_file:
            xunit_file.write(self.generate())

    def processCaseRunFinished(self, testCaseID):
        pass
