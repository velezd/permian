import abc
from .grouped import GroupedWorkflow

class IsolatedWorkflow(GroupedWorkflow):
    """
    Abstract class for workflows which goal is to execute caseRunConfiguration
    instances separately and no grouping of execution is desired.

    This class provides additional methods related to the only one
    caseRunConfiguration it's handling. See methods which name doesn't start
    with 'group'.

    Workflow instances should not be directly created, use the factory method
    which should handle creation of the workflow instances.
    """
    @classmethod
    def factory(cls, caseRunConfigurations):
        """
        Make instances of this workflow for given caseRunConfigurations and
        assign them accordingly.

        The IsolatedWorkflow implementation of this factory makes separate
        instance for each caseRunConfiguration object where each of the
        instances is handling exactly one caseRunConfiguration object.

        :param caseRunConfigurations: List of CaseRunConfiguration which belong to this workflow.
        :type caseRunConfigurations: list
        :return: None
        :rtype: None
        """
        for caseRunConfiguration in caseRunConfigurations:
            cls(caseRunConfiguration)

    def __init__(self, caseRunConfiguration):
        self.caseRunConfiguration = caseRunConfiguration
        super().__init__([caseRunConfiguration])

    def _check_caseConfigurations(self, caseRunConfigurations):
        """
        Function helping to decide if provided caseRunConfigurations are
        valid for this workflow.
        """
        if [self.caseRunConfiguration] != caseRunConfigurations:
            raise ValueError('Unknown configuration provided')

    def groupTerminate(self, caseRunConfigurations):
        """
        Terminate all matching caseRunConfigurations which in case of
        Isolated workflow is the only one it's handling. If the
        caseRunConfigurations doesn't contain just the one valid for this
        workflow, throw exception.

        :raises ValueError: If invalid caseRunConfigurations is provided
        :return: True if the workflow was terminated False otherwise
        :rtype: bool
        """
        self._check_caseConfigurations(caseRunConfigurations)
        return self.terminate()

    @abc.abstractmethod
    def terminate(self):
        """
        Process termination of this workflow.

        :return: True if the workflow was terminated False otherwise
        :rtype: bool
        """

    def reportResult(self, result):
        """
        Shortcut method for groupReportResult. The caseRunConfigurations
        is not needed when this method is used.
        """
        super().groupReportResult([self.caseRunConfiguration], result)

    def groupDisplayStatus(self, caseRunConfiguration):
        """
        Provide displayStatus of the given caseRunConfiguration which in case
        of Isolated workflow is the only one it's handling. If the
        caseRunConfiguration doesn't match the one valid for this workflow,
        throw exception.

        :raises ValueError: If invalid caseRunConfiguration is provided
        :return: Markdown formatted string to be displayed for user
        :rtype: str
        """
        self._check_caseConfigurations([caseRunConfiguration])
        return self.displayStatus()

    @abc.abstractmethod
    def displayStatus(self):
        """
        Provides displayStatus string of this workflow.

        :return: Markdown formatted string to be displayed for user
        :rtype: str
        """
