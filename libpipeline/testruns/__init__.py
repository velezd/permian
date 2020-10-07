from hashlib import sha1
from functools import lru_cache
import logging

from ..exceptions import UnexpectedState, NotReady, StateChangeError, UnknownTestConfigurationMergeMethod
from ..workflows.factory import WorkflowFactory
from ..resultsrouter import ResultsRouter
from .result import UNSET, STATES, RESULTS

LOGGER = logging.getLogger(__name__)

class TestRuns():
    """Collection of case-run-configurations based on the Test Plans, Requirements and Test Cases from tclib provided library.

    This class also handles assignment of the workflows and manages their
    execution.
    """
    def __init__(self, library, event, settings):
        self.caseRunConfigurations = []
        """List of CaseRunConfigurations taking part in this execution"""
        self.populateCaseRunConfigurations(library, event, settings)
        self.assignWorkflows(event, settings)
        self.resultsRouter = ResultsRouter(self, library, event, settings)

    def populateCaseRunConfigurations(self, library, event, settings):
        """
        Based on the event and settings takes Test plans from library and
        for each of the Test plans collects list of Test cases and their
        configurations (in the context of the test plan). Based on those
        creates CaseRunConfiguration objects and stores them in
        caseRunConfigurations for later execution.

        If multiple caseRunConfiguration object share same testcase and
        configuration, they are merged into one object keeping records
        of the Test plans the case-run-configurations belong to.
        """
        self.caseRunConfigurations = event.generate_caseRunConfigurations(library, settings)
        for caserun in self.caseRunConfigurations:
            caserun.testrun = self

    def assignWorkflows(self, event, settings):
        """
        Aggregate CaseRunConfiguration objects based on their workflows
        and call Workflows factory function which then takes care of creating
        desired Worklflow instances. The Workflow instances are responsible
        for assigning themselves (as they see fit) to the CaseRunConfiguration
        objects. Note that one Workflow can be assigned to multiple
        CaseRunConfiguration objects.

        :raises UnexpectedState: When there's at least one CaseRunConfiguration object without workflow assigned.
        :return: None
        :rtype: None
        """
        WorkflowFactory.assign(self, event, settings)

    def start(self):
        """
        Run start method on all workflows assigned to the CaseRunConfiguration
        objects.

        Note there may be multiple CaseRunConfiguration objects sharing the
        same Workflow object. In such situation, the start method should be
        called for one Workflow object only once.

        If this start method was already successfully invoked, nothing should
        happen.

        :raises NotReady: When this method is called before workflows are assigned.
        :return: None
        :rtype: None
        """
        self.resultsRouter.start()
        for caserun in self.caseRunConfigurations:
            caserun.workflow.start()
        # TODO: notify ResultsCollector
        # TODO: start workflows

    def wait(self):
        """
        Block execution until all workflows are finished. If this method is
        called after all workflows are finished, nothing should happen and no
        blocking should occur.

        :raises NotReady: When start method was not invoked yet.
        :return: None
        :rtype: None
        """
        # TODO: wait for workflows
        self.resultsRouter.wait()

    # TODO: consider using functools.lru_cache or functools.cached_property
    @property
    def testPlansMapping(self):
        """
        Mapping of testPlans to caseRunConfigurations. The keys are TestPlan
        ids and values are caseRunConfigurations which belong to the TestPlan.
        """
        result = {}
        for caserunconfiguration in self.caseRunConfigurations:
            for testplan in caserunconfiguration.running_for:
                try:
                    result[testplan].append(caserunconfiguration)
                except KeyError:
                    result[testplan] = [caserunconfiguration]
        return result

class CaseRunConfiguration():
    """Representation of case-run-configuration containing logic for state and
    result management as well as information about workflow responsible for
    handling of the case-run-configuration.

    :param testcase: Test case for which the case-run is executed.
    :type testcase: tclib.structures.testcase.TestCase
    :param configuration: Configuration for which the case-run is executed.
    :type configuration: dict
    :param testplans: List of testplan ids for which the case-run-configuration executed.
    :type testplans: list
    """
    def __init__(self, testcase, configuration, testplans):
        self.testrun = None
        self.testcase = testcase
        """TestCase handled by this run"""
        self.configuration = configuration
        """Configuration of the TestCase"""
        self.running_for = { testplan.id : True for testplan in testplans }
        """Mapping of plans for which this configuration shoud be executed"""
        self.workflow = None
        """Workflow instance handling execution of this configuration"""
        from .result import Result # TODO, remove this ugly import during refactoring
        self.result = Result('not started')
        """TODO"""

    @property
    @lru_cache(maxsize=None)
    def id(self):
        """ Return string ID made from hash """
        return sha1(str(self.__hash__()).encode()).hexdigest()

    def copy(self):
        caserun = CaseRunConfiguration(self.testcase, self.configuration, [])
        caserun.running_for = self.running_for
        caserun.workflow = self.workflow
        caserun.result = self.result.copy()
        return caserun

    def cancel(self, reason, testplan_id=None):
        """
        Attempt to cancel this case-run-configuration either for all testplans
        or for specific testplan. The workflow cancel is invoked once there's
        no testplan for which the case-run-configuration would run.

        :param reason: Description why the cancel should happen.
        :type reason: str
        :param testplan_id: Identifier of the testplan for which the case-run-configuration should be canceled, defaults to None
        :type testplan_id: str, optional
        :raises StateChangeError: When attempting to cancel already canceled or in other way ended test-run-configuration
        :return: True if the workflow cancel was invoked
        :rtype: bool
        """
        if testplan_id is not None:
            self.running_for[testplan_id] = False
            if any(self.running_for.values()):
                return False
            self.workflow.cancel(self)
            # TODO: record reason
            from .result import Result # TODO, remove this ugly import during refactoring
            self.updateResult(Result('canceled', None, True))
            return True
        else:
            for testplan_id in self.running_for:
                if self.cancel(reason, testplan_id):
                    return True
        raise UnexpectedState()

    def updateResult(self, result):
        """
        Update state of this case-run-configuration optionally setting result
        as well. This method is also used to mark the state as final effectively
        preventing any further change.

        :param state: Desired state to be set
        :type state: str
        :param result: Desired result to be set. If result is not set, the result is not changed. defaults to UNSET
        :type result: str, optional
        :param final: Mark the state as final preventing any future changes.
        :type final: bool
        :raises ValueError: When unknown state or result is provided.
        :return: None
        :rtype: None
        """
        result = result.copy()
        result.caseRunConfiguration = self
        # TODO: lock when changing status
        LOGGER.debug('Attempting to change result of "%s" from %s to %s', self.id, self.result, result)
        try:
            self.result.update(result)
            self.testrun.resultsRouter.routeResult(result)
        except StateChangeError as e:
            LOGGER.error('Cannot change state of result: %s', e)
        # TODO: unlock
        # TODO: provide self.result.copy() to TestRun/ResultsCollector

    def assignWorkflow(self, workflow):
        """
        If workflow is already assigned and different workflow is about
        to assigned, raise traceback.

        While locked(state):
        If the state None, assign workflow and change state to queued.

        :param workflow: Mark this workflow as the one handling this case-run-configuration.
        :type workflow: tclib.Workflow
        :raises ValueError: When a different workflow instance is assigned.
        :return: None
        :rtype: None
        """

    def __iadd__(self, other):
        """
        Custom implementation of += operator.

        If the same CaseRunConfiguration is provided, update the information
        of Test Plans in this instance taking the Test Plans from the other
        instance.

        :raises NotImplemented: When object of incompatible type is given
        :raises ValueError: When not matching CaseRunConfiguration is given
        :return: self
        :rtype: CaseRunConfiguration
        """
        if not isinstance(other, CaseRunConfiguration):
            raise NotImplementedError()
        if self != other:
            raise ValueError("Cannot merge different CaseRunConfigurations")
        self.running_for.update(other.running_for)
        return self

    def __eq__(self, other):
        """
        Custom implementation of == operator.

        Compare with other CaseRunConfiguration and if they are of the same
        testcase and configuration return True.

        If the type of other is different fallback to other python methods
        allowing for other to still consider itself being the same thing.

        :raises NotImplemented:
        :return: True if the other CaseRunConfiguration is for the same testcase and has the same configuration, False otherwise.
        :rtype: bool
        """
        if not isinstance(other, CaseRunConfiguration):
            raise NotImplementedError()
        return (self.testcase, self.configuration) == (other.testcase, other.configuration)

    def __hash__(self):
        """ Returns hash of the CaseRunConfiguration made from testcase and configuration """
        return hash((self.testcase, tuple(sorted(self.configuration.items()))))

    def __repr__(self):
        return f"<CaseRunConfiguration({self.testcase.name}:{self.configuration})>"

class CaseRunConfigurationsList(list):
    """ Special list object with modified behaviour of append method for use with CaseRunConfigurations """
    def append(self, other_caserun):
        # If CaseRunConfiguration already created add current testplan to its running_for
        if other_caserun in self:
            self[self.index(other_caserun)] += other_caserun
        else:
            super().append(other_caserun)


class ConfigurationDictHybrid(dict):
    """ Configuration dict that tries to combine configurations while respecting limitations """
    def merge(self, other):
        """ Merges self and other dict by preserving key-values from other dict and adding unique keys from self """
        config = other.copy()
        for missing_key in self.keys() - other.keys():
            config[missing_key] = self[missing_key]
        return config

    def compatible_with(self, other):
        """ Checks if this configuration dict can be merged with other dict using the Hybrid method:
        all keys that are in both dicts must have the same value
        """
        for key, value in self.items():
            if key in other and value != other[key]:
                return False
        return True

class ConfigurationDictStrict(dict):
    """ Configuration dict that 'merges' only exactly the same configurations """
    def merge(self, other):
        """ Just returns other dict as it has to be the same in order to be 'merged' """
        return other

    def compatible_with(self, other):
        """ Checks if this configuration dict can be merged with other dict using the Strict method:
        must be the same
        """
        return self == other

class ConfigurationsList(list):
    def __init__(self, clist, merge_method):
        """ List of configurations used for testplan that then extends and/or limits testcase configurations during merge

        :param clist: (Testplan) Configurations
        :type clist: list of dicts, None
        :param merge_method: name of merge method - determines the type of configurations
        :type merge_method: string
        """
        # Handle None configurations list
        if clist is None:
            clist = []
        # Conver configurations to particular ConfigurationDict based on merge_method
        if merge_method == 'intersection':
            clist = [ ConfigurationDictStrict(item) for item in clist ]
        elif merge_method == 'extension':
            clist = [ ConfigurationDictHybrid(item) for item in clist ]
        else:
            raise UnknownTestConfigurationMergeMethod(merge_method)
        super().__init__(clist)

    def merge(self, other):
        """ Merges self configurations and other configurations
        If self configurations is empty, the other configurations are returned
        If other configurations is empty, empty dict is added

        :param testcase: Testcase
        :type testcase: tclib.TestCase
        :param testplan: Testplan
        :type testplan: tclib.TestPlan
        :return: Configurations
        :rtype: list of dicts
        """
        configs = []
        # Handle no other configurations
        if other == None:
            other = [{}]
        # Handle no self configurations
        if self == []:
            return other
        # Perform merge
        for self_config in self:
            for other_config in other:
                if self_config.compatible_with(other_config):
                    configs.append(self_config.merge(other_config))

        return configs

def merge_testcase_configurations(caseRunConfigurations):
    """ Converts list of CaseRunConfiguration objects into a dict with testcase name as key
    and adds common result and workflow

    :param caseRunConfigurations: List of CaseRunConfiguration objects
    :type caseRunConfigurations: list
    :raises RuntimeError: When workflow is not common for all configurations of a testcase
    :return: {'testcase_name': {caseRunConfigurations: list, result: Result, workflow: str}, ...}
    :rtype: dict
    """
    testcases = {}
    for caserun in caseRunConfigurations:
        if caserun.testcase.name not in testcases:
            testcases[caserun.testcase.name] = {'caseRunConfigurations': [], 'result': None, 'workflow': None}
        testcase = testcases[caserun.testcase.name]

        # add caserun
        testcase['caseRunConfigurations'].append(caserun)
            
        # set workflow
        if testcase['workflow'] is not None and testcase['workflow'] != caserun.testcase.execution['type']:
            raise RuntimeError('CaseRunConfigurations for one tescase have different workflows')
        testcase['workflow'] = caserun.testcase.execution['type']
            
        if testcase['result'] is None:
            testcase['result'] = caserun.result.copy()
            continue

        from .result import STATES, RESULTS # TODO, remove this ugly import during refactoring
        if list(STATES).index(testcase['result'].state) > list(STATES).index(caserun.result.state):
            testcase['result'].state = caserun.result.state
        if list(RESULTS).index(testcase['result'].result) < list(RESULTS).index(caserun.result.result):
            testcase['result'].result = caserun.result.result

    return testcases
