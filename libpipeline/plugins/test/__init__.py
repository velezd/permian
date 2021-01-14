import logging
import json
import re
from os import path
from time import sleep
from .. import api
from ...workflows.isolated import IsolatedWorkflow
from ...result import Result, STATES, RESULTS, UNSET
from ...events.base import Event 
from ...reportsenders.base import BaseReportSender


LOGGER = logging.getLogger(__name__)


@api.cli.register_command_parser('test')
def test_command(base_parser, args):
    parser = base_parser
    parser.add_argument('--tp', action='append', required=True,
                        help='Name of testplan to execute - can be used multiple times')
    options = parser.parse_args(args)
    return options, json.dumps({'type': 'test', 'test': {'testplans': options.tp}})


@api.events.register_structure('test')
class TestStructure():
    def __init__(self, testplans):
        self.testplans = testplans

@api.events.register('test')
class TestEvent(Event):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_testplans = self.test.testplans


@api.workflows.register("test")
class TestWorkflow(IsolatedWorkflow):
    def __init__(self, testRuns, crcList):
        super().__init__(testRuns, crcList)
        self.status_step_counter = 0
        self.terminated = False

    def formatLogMessage(self, message):
        return self.logFormat.format(
            message=message,
            asctime=self.status_step_counter,
        )

    def execute(self):
        last_state = None
        # initial delay - to ensure specific order of results in reporting
        sleep(self.crc.configuration.get('initial_delay', 0) + (self.crc.configuration.get('test', 0) * 0.01))

        for num, step in enumerate(self.crc.testcase.execution.automation_data, start=1):
            self.log(f'Running step no {num}: {step}')
            if self.terminated: break
            self.status_step_counter = num
            state = step.get('state', last_state)
            result = step.get('result', None)
            final = step.get('final', False)

            if self.terminated: break
            if 'log' in step:
                for logname, message in step['log'].items():
                    self.log(f"Writing message to log: {logname}")
                    self.log(message, logname)

            if self.terminated: break
            if 'log_file' in step:
                for logname, log_path in step['log_file'].items():
                    self.log(f"Adding log {logname} pointing to: {log_path}")
                    self.addLog(logname, log_path)

            if self.terminated: break
            if 'sleep' in step:
                self.log(f"Sleeping: {step['sleep']}")
                sleep(step['sleep'])

            if self.terminated: break
            if {'state', 'result', 'final'}.intersection(step.keys()):
                self.log(f"Reporting Result({state}, {result}, {final})")
                self.reportResult(Result(state, result, final))
                last_state = state

    def terminate(self):
        self.terminated = True
        return True

    def displayStatus(self):
        return 'Processing step: ' + str(self.status_step_counter)


@api.reportsenders.register('test')
class TestReportSender(BaseReportSender):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.processing_log_filename = path.join(self.settings.get('testingPlugin', 'reportSenderDirectory'),
                                                 self.reporting.data.get('filename', re.sub(r'[^\w\d-]', '_', self.testplan.name)))
        if self.group is not None:
            self.processing_log_filename += f'-{self.group!r}'
        self.processing_log_file = None

    def setUp(self):
        self.processing_log_file = open(self.processing_log_filename, 'w')

    def tearDown(self):
        self.processing_log_file.close()

    def processPartialResult(self, crc):
        self.processing_log_file.write('reporter %s - result partial %s-%s - %s, %s, %s\n' % (self.reporting.data.get('reporter', 0),
            crc.testcase.name,
            crc.configuration.get('test', 0),
            crc.result.state, crc.result.result, crc.result.final))

    def processFinalResult(self, crc):
        self.processing_log_file.write('reporter %s - result final %s-%s - %s, %s, %s\n' % (self.reporting.data.get('reporter', 0),
            crc.testcase.name,
            crc.configuration.get('test', 0),
            crc.result.state, crc.result.result, crc.result.final))

    def processTestRunStarted(self):
        self.processing_log_file.write('reporter %s - testrun "%s" started\n' % (self.reporting.data.get('reporter', 0),
            self.testplan.name))

    def processTestRunFinished(self):
        self.processing_log_file.write('reporter %s - testrun "%s" finished\n' % (self.reporting.data.get('reporter', 0),
            self.testplan.name))

    def processCaseRunFinished(self, testCaseID):
        self.processing_log_file.write('reporter %s - finished testcase "%s" in "%s"\n' % (self.reporting.data.get('reporter', 0),
            testCaseID, self.testplan.name))
