from .xunit import BaseXunitReportSender
from .. import api
from os import path
import re


@api.reportsenders.register('xunit')
class XunitReportSender(BaseXunitReportSender):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.xunit_filename = self._xunit_filename()

    def processPartialResult(self, crc):
        pass

    def processFinalResult(self, crc):
        pass

    def processTestRunStarted(self):
        pass

    def processTestRunFinished(self):
        with open(path.join(self.settings.get('reportSenders', 'reporting_dir'), self.xunit_filename), 'w') as xunit_file:
            xunit_file.write(self.generate())

    def processCaseRunFinished(self, testCaseID):
        pass

    def _xunit_filename(self):
        group_string = ''
        if self.group:
            group_string = ';'.join([ f'{key}:{value}' for key, value in self.group.items() ])
            # Make configuration values filename safe
            group_string = '-' + re.sub(r'/', '', group_string)

        return 'xunit-%s%s.xml' % (re.sub(r'/', '_', self.testplan.name), group_string)
