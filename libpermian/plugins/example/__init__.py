import json
import logging
import time

from .. import api
from ...workflows.isolated import IsolatedWorkflow, GroupedWorkflow
from ...events.base import Event
from ...reportsenders.base import BaseReportSender
from libpermian.result import Result

LOGGER = logging.getLogger(__name__)

@api.workflows.register("example")
class ExampleWorkflow(IsolatedWorkflow):
    def setup(self):
        '''
        This method is executed before the execute (or dry_execute) method.
        The default implementation of this method doesn't do anything.
        Anything that is needs to be done prior to the execution
        (preprocessing data, obtaining required data, waiting for resources to
        be ready) belongs to this method.
        '''
        # report progress - the execution hasn't started yet, but preparation
        # activities has started
        self.reportResult(Result('queued'))

    def execute(self):
        '''
        This method contains steps that are done as part of the execution of
        the test case. This method must to be implemented.
        '''
        # report progress of the execution
        self.reportResult(Result('started'))
        LOGGER.info("Let's rock!")
        self.reportResult(Result('running'))
        # log message
        self.log('This message will be logged to wokflow.txt')
        self.log('This message will be logged to foo.txt', 'foo')
        # add local log file
        self.addLog('host_cpuinfo.txt', '/proc/cpuinfo')
        # add remote log file
        self.addLog('gpl-3.0.txt', 'https://www.gnu.org/licenses/gpl-3.0.txt')
        # Access automation data
        self.log(
            'Automation data is: %s' %
            self.crc.testcase.execution.automation_data
        )

    def dry_execute(self):
        '''
        Method that is executed instead of execute if pipeline is configured
        to run workflows in dry_run mode.
        '''
        pass

    # teardown doesn't have to be implemented and it's up to the workflow
    # when the final result will be reported
    def teardown(self):
        '''
        Similar as setup method, this method should contain any cleanup code
        that's needed to be done after the execution ends.
        Note that there's no hard requirement for the teardown to report
        results and the final result can very well be provided by the execute
        method.
        '''
        # report progress
        self.reportResult(Result('cleaning'))
        self.reportResult(Result('complete', 'PASS', final=True))

    def terminate(self):
        '''
        This method is asynchronously invoked while setup/execute/teardown
        methods are running in different thread. It can be invoked only if
        final result was not provided.
        This method should contain code that would stop the execution of
        setup/execute/teardown methods of this (Threading) instance. It's up
        to the workflow how this is achieved.
        Note that no result should be reported as "cancelled" final state is
        set as part of the terminate invocation.
        '''
        LOGGER.info('Something attempted to stop me!')
        return False

    def displayStatus(self):
        '''
        This method is asynchronously called while setup/execute/teardown
        methods are running in different thread.
        This method provides status (as Markdown formatted string) that's
        displayed in the WebUI for end user.
        '''
        return 'This is example workflow'

@api.workflows.register("multiple_example")
class MultipleExampleWorkflow(GroupedWorkflow):
    @classmethod
    def factory(cls, testRuns, crcList):
        '''
        Decide which crcs will be executed together in one instance.
        This method constructs the instances of the class in a way that each
        crc in the given crcList must be provided to exactly one instance of
        this class.
        '''
        # Create instance for each testcase separately, one instance will
        # handle execution of multiple different configurations (architectures)
        # of the test case.
        for testcase, crcs in crcList.by_testcase():
            cls(testRuns, crcs)

    def setup(self):
        '''
        Same as ExampleWorkflow.setup
        '''
        # report progress - the execution hasn't started yet, but preparation
        # activities has started for all handled crcs
        self.groupReportResult(self.crcList, Result('queued'))

    def execute(self):
        '''
        Same as ExampleWorkflow.execute
        '''
        # report progress of the execution
        self.groupReportResult(self.crcList, Result('started'))
        LOGGER.info("Let's rock!")
        self.groupReportResult(self.crcList, Result('running'))
        # log message
        self.groupLog('This message will be logged to wokflow.txt for all crcs')
        self.groupLog(
            'This message will be logged to wokflow.txt for first crc',
            crcList=list(self.crcList[0]),
        )
        self.groupLog(
            'This message will be logged to foo.txt for all crcs',
            'foo',
        )
        # add local log file
        self.groupAddLog('host_cpuinfo.txt', '/proc/cpuinfo')
        # add remote log file for first crc
        self.groupAddLog(
            'gpl-3.0.txt',
            'https://www.gnu.org/licenses/gpl-3.0.txt',
            crcList=list(self.crcList[0]),
        )

    def dry_execute(self):
        '''
        Same as ExampleWorkflow.dry_execute
        '''
        pass

    # teardown doesn't have to be implemented and it's up to the workflow
    # when the final result will be reported
    def teardown(self):
        '''
        Same as ExampleWorkflow.teardown
        '''
        # report progress
        self.groupReportResult(self.crcList, Result('cleaning'))
        self.groupReportResult(
            self.crcList,
            Result('complete', 'PASS', final=True),
        )

    def groupTerminate(self, crcIds):
        '''
        Similar as ExampleWorkflow.terminate, but only provided crcs with ids
        from crcIds are to be terminated.
        '''
        LOGGER.info('Something attempted to stop me!')
        return False

    def groupDisplayStatus(self, crcId):
        '''
        Similar as ExampleWorkflow.displayStatus, but the status if only of
        the crc with given crcId.
        '''
        return 'This is example workflow running: %s' % crcId

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
