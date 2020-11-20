import abc
import threading

from ..exception_dump import dump_exception
from ..result import Result


class GroupedWorkflow(threading.Thread, metaclass=abc.ABCMeta):
    """
    Abstract class for all workflows. Use this class as parent for you
    workflow if you want to handle multiple caseRunConfigurations by one
    workflow instance. If you're not seeking this functionality, look for
    IsolatedWorkflow class.

    Workflow instances should not be directly created, use the factory method
    which should handle creation of the workflow instances.
    """
    @classmethod
    @abc.abstractmethod
    def factory(cls, testRuns, crcList):
        """
        Make instances of this workflow for given caseRunConfigurations and
        assign them accordingly.

        Note: Once same instance may be assigned to multiple items of
        caseRunConfigurations. The way how the instances are assigned to
        individual caseRunConfiguration objects is up to the workflow.

        :param crcIds: List of CaseRunConfiguration which belong to this workflow.
        :type crcIds: list
        :return: None
        :rtype: None
        """

    def __init__(self, testRuns, crcList):
        self.testRuns = testRuns
        self.event = testRuns.event
        self.settings = testRuns.settings
        self.dryRun = self.settings.getboolean('workflows', 'dry_run')
        self.exceptions = []
        for crc in crcList:
            crc.workflow = self
        self.crcList = crcList.copy()
        super().__init__()

    def run(self):
        """
        This is the main body of the workflow execution. This method calls
        setup, execute (or dry_execute) and teardown methods in sequence.

        This method is not meant to be called directly as it's started in
        separate thread once the workflow.start method is invoked. For more
        information see Threading.Thread.start.

        :return: None
        :rtype: None
        """
        try:
            self.setup()
            self.execute() if not self.dryRun else self.dry_execute()
        except Exception as e:
            self.exceptions.append(dump_exception(e, self))
            self.groupReportResult(self.crcList, Result('DNF', 'ERROR', True))
        try:
            self.teardown()
        except Exception as e:
            self.exceptions.append(dump_exception(e, self))

    def setup(self):
        """
        Steps performed before actual execution started.

        :return: None
        :rtype: None
        """
        # do some preparation and logging

    @abc.abstractmethod
    def execute(self):
        """
        Steps performed during the execution of the workflow. Here's the place
        where the core code of the workflow should be happening.

        This method should NEVER EVER perform any computation intensive tasks
        as it's executed in python thread. If needed, use separate processes
        using subprocess, multiprocessing modules or fork function.

        :return: None
        :rtype: None
        """

    def dry_execute(self):
        """
        This method is invoked instead of the execute when the
        caseRunConfiguration should be executed in dry_run mode.
        """

    def teardown(self):
        """
        Steps performed after the execution ended.

        :return: None
        :rtype: None
        """
        # do some afteractions and logging

    @abc.abstractmethod
    def groupTerminate(self, crcIds):
        """
        Terminate execution of specific crcIds handled by the
        workflow.

        :param crcIds: Configurations to be terminated
        :type crcIds: list
        :return: TODO
        :rtype: TODO
        """

    def groupReportResult(self, crcList, result):
        """
        Provide partial or final result for the crcId. For more
        information see TODO:Result.

        :param crcIds: TODO
        :type crcIds: list
        :param result: TODO
        :type result: TODO
        :return: None
        :rtype: None
        """
        for crc in crcList:
            crc.updateResult(result)
            self.testRuns.update(crc)

    def groupGetLog(self, crcId, log_type):
        """
        Return log of the log_type associated to the crcId.

        :param crcId: TODO
        :type crcId: str
        :param log_type: TODO
        :type log_type: str or None
        :return: Content of the log
        :rtype: str
        """

    @abc.abstractmethod
    def groupDisplayStatus(self, crcId):
        """
        Provides more comprehensive (and possibly graphically formatted) status
        of the workflow for the end user. This is meant as channel where more
        advanced information such as hyperlink to external system with some
        brief description of current workflow state is provided.

        Note: Output of this method should never be parsed.

        :param crcIds:
        :type crcIds:
        :return: Markdown formatted text provided for human processing
        :rtype: str
        """

