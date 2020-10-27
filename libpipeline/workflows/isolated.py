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
    def factory(cls, testRuns, crcIds):
        """
        Make instances of this workflow for given crcIds and
        assign them accordingly.

        The IsolatedWorkflow implementation of this factory makes separate
        instance for each caseRunConfiguration object where each of the
        instances is handling exactly one caseRunConfiguration object.

        :param crcIds: List of CaseRunConfiguration which belong to this workflow.
        :type crcIds: list
        :return: None
        :rtype: None
        """
        for crcId in crcIds:
            cls(testRuns, crcId)

    def __init__(self, testRuns, crcId):
        self.crcId = crcId
        super().__init__(testRuns, [crcId])

    def _check_caseConfigurations(self, crcIds):
        """
        Function helping to decide if provided crcIds are
        valid for this workflow.
        """
        if [self.crcId] != crcIds:
            raise ValueError('Unknown configuration provided')

    def groupTerminate(self, crcIds):
        """
        Terminate all matching crcIds which in case of
        Isolated workflow is the only one it's handling. If the
        crcIds doesn't contain just the one valid for this
        workflow, throw exception.

        :raises ValueError: If invalid crcIds is provided
        :return: True if the workflow was terminated False otherwise
        :rtype: bool
        """
        self._check_caseConfigurations(crcIds)
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
        Shortcut method for groupReportResult. The crcIds
        is not needed when this method is used.
        """
        super().groupReportResult([self.crcId], result)

    def groupDisplayStatus(self, crcId):
        """
        Provide displayStatus of the given crcId which in case
        of Isolated workflow is the only one it's handling. If the
        crcId doesn't match the one valid for this workflow,
        throw exception.

        :raises ValueError: If invalid crcId is provided
        :return: Markdown formatted string to be displayed for user
        :rtype: str
        """
        self._check_caseConfigurations([crcId])
        return self.displayStatus()

    @abc.abstractmethod
    def displayStatus(self):
        """
        Provides displayStatus string of this workflow.

        :return: Markdown formatted string to be displayed for user
        :rtype: str
        """
