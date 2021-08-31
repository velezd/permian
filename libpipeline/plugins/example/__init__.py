import json
import logging
import time

from .. import api
from ...workflows.isolated import IsolatedWorkflow
from ...events.base import Event
from ...reportsenders.base import BaseReportSender

LOGGER = logging.getLogger(__name__)

@api.workflows.register("example")
class ExampleWorkflow(IsolatedWorkflow):
    def execute(self):
        LOGGER.info("Let's rock!")
        # TODO: result should be returned here

    def terminate(self):
        LOGGER.info('Something attempted to stop me!')
        return False

    def displayStatus(self):
        return 'This is example workflow'

# TODO: Provisioners are currently not implemented
@api.register_provisioner
class ExampleProvisioner():
    pass

@api.reportsenders.register
class ExampleReportSender(BaseReportSender):
    def processPartialResult(self, result):
        LOGGER.info('Got partial result: %r', result)

    def processFinalResult(self, result):
        LOGGER.info('Got final result: %r', result)

    def processTestRunStarted(self):
        LOGGER.info('My TestRun just started.')

    def processTestRunFinished(self):
        LOGGER.info('My TestRun just finished')

    def processCaseRunFinished(self, testCaseID):
        LOGGER.info('CaseRun of this TestCase is now completely finished: %r', testCaseID)

# TODO: ResultsProcessors are currently not implemented
@api.register_resultsProcessor
class ExampleResultsProcessor():
    pass

@api.events.register('example')
class ExampleEvent(Event):
    def __init__(self, settings, event_type, **kwargs):
        super().__init__(settings, event_type, **kwargs)
        example_hook('Hello from Event constructor')

@api.hooks.make
def example_hook(msg):
    pass

# let's call threaded callback first
@api.hooks.threaded_callback_on(example_hook)
def example_threaded_callback(msg):
    time.sleep(0.5)
    LOGGER.info('(threaded) Example hook says: %r' % msg)

@api.hooks.callback_on(example_hook)
def example_callback(msg):
    LOGGER.info('Example hook says: %r' % msg)
    LOGGER.debug("And here's also a debug message!")
    time.sleep(1)

@api.cli.register_command_parser('example')
def example_command(base_parser, args):
    options = base_parser.parse_args(args)
    return options, json.dumps({'type': 'example'})

@api.cli.register_command_args_extension
def example_argparse_extension(parser):
    parser.add_argument('--example-argument', action='store_true')
    return parser
