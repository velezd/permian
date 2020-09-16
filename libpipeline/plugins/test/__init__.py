import logging

import json
from time import sleep
from .. import api
from ...workflows.isolated import IsolatedWorkflow
from ...testruns.result import Result, STATES, RESULTS, UNSET
from ...events.base import Event 
from ...reportsenders.base import BaseReportSender


LOGGER = logging.getLogger(__name__)


@api.cli.register_command_parser('test')
def test_command(base_parser, args):
    parser = base_parser
    parser.add_argument('--tp', action='append', required=True,
                        help='Name of testplan to execute - can be used multiple times')
    options = parser.parse_args(args)
    return options, json.dumps({'type': 'test', 'payload': {'testplans': options.tp}})


@api.events.register('test')
class TestEvent(Event):
    def __init__(self, event_type, payload, other_data):
        print(event_type, payload, other_data)
        super().__init__(event_type, payload, other_data)
        self.selected_testplans = payload['testplans']


@api.workflows.register("test")
class TestWorkflow(IsolatedWorkflow):
    def __init__(self, caseRunConfiguration, event, settings):
        super().__init__(caseRunConfiguration, event, settings)
        self.status_step_counter = 0
        self.terminated = False

    def execute(self):
        last_state = None
        for num, step in enumerate(self.caseRunConfiguration.testcase.execution.automation_data, start=1):
            if self.terminated: break
            self.status_step_counter = num
            state = step.get('state', last_state)
            result = step.get('result', None)
            final = step.get('final', False)

            if self.terminated: break
            if 'sleep' in step:
                sleep(step['sleep'])

            if self.terminated: break
            if {'state', 'result', 'final'}.intersection(step.keys()):
                self.reportResult(Result(state, result, final))
                last_state = state

    def terminate(self):
        self.terminated = True
        self.reportResult(Result('canceled', None, True))
        return True

    def displayStatus(self):
        return 'Processing step: ' + str(self.status_step_counter)


@api.reportsenders.register('test')
class TestReportSender(BaseReportSender):
    """ Placeholder ReportSender """
    def processPartialResult(self, result):
        LOGGER.debug('%s reporting partial result: %s', self, result)

    def processFinalResult(self, result):
        LOGGER.debug('%s reporting final result %s', self, result)

    def processTestRunStarted(self):
        LOGGER.debug('%s reporting Test Run started', self)

    def processTestRunFinished(self):
        LOGGER.debug('%s reporting Test Run finished', self)

    def processCaseRunFinished(self, testCaseID):
        LOGGER.debug('%s reporting Case Run of "%s" finished', self, testCaseID)

    def wait(self):
        pass
