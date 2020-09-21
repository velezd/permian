import abc
import threading

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
    def factory(cls, caseRunConfigurations, event, settings):
        """
        Make instances of this workflow for given caseRunConfigurations and
        assign them accordingly.

        Note: Once same instance may be assigned to multiple items of
        caseRunConfigurations. The way how the instances are assigned to
        individual caseRunConfiguration objects is up to the workflow.

        :param caseRunConfigurations: List of CaseRunConfiguration which belong to this workflow.
        :type caseRunConfigurations: list
        :return: None
        :rtype: None
        """

    def __init__(self, caseRunConfigurations, event, settings):
        self.event = event
        self.settings = settings
        self.dryRun = self.settings.getboolean('workflows', 'dry_run')
        self.caseRunConfigurations = caseRunConfigurations
        for caseRunConfiguration in caseRunConfigurations:
            caseRunConfiguration.workflow = self
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
        self.setup()
        self.execute() if not self.dryRun else self.dry_execute()
        self.teardown()

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
    def groupTerminate(self, caseRunConfigurations):
        """
        Terminate execution of specific caseRunConfigurations handled by the
        workflow.

        :param caseRunConfigurations: Configurations to be terminated
        :type caseRunConfigurations: list
        :return: TODO
        :rtype: TODO
        """

    def groupReportResult(self, caseRunConfigurations, result):
        """
        Provide partial or final result for the caseRunConfiguration. For more
        information see TODO:Result.

        :param caseRunConfigurations: TODO
        :type caseRunConfigurations: list
        :param result: TODO
        :type result: TODO
        :return: None
        :rtype: None
        """
        for caseRunConfiguration in caseRunConfigurations:
            caseRunConfiguration.updateResult(result)

    def groupGetLog(self, caseRunConfiguration, log_type):
        """
        Return log of the log_type associated to the caseRunConfiguration.

        :param caseRunConfiguration: TODO
        :type caseRunConfiguration: caseRunConfiguration
        :param log_type: TODO
        :type log_type: str or None
        :return: Content of the log
        :rtype: str
        """

    @abc.abstractmethod
    def groupDisplayStatus(self, caseRunConfiguration):
        """
        Provides more comprehensive (and possibly graphically formatted) status
        of the workflow for the end user. This is meant as channel where more
        advanced information such as hyperlink to external system with some
        brief description of current workflow state is provided.

        Note: Output of this method should never be parsed.

        :param caseRunConfiguration:
        :type caseRunConfiguration:
        :return: Markdown formatted text provided for human processing
        :rtype: str
        """

