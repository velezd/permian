import functools
from ..caserunconfiguration import CaseRunConfiguration, ConfigurationsList, CaseRunConfigurationsList
from tclib.expressions import eval_bool
#from ..exceptions import UnknownEventSubTypeExpression

from .functions import dotted_startswith
from .structures.factory import EventStructuresFactory

class Event():
    """
    Base class of event which stores its type, event structures (automatically
    provides converted event structures) and decides which testplans and
    caserunconfigurations will be executed based on the event.

    This base class can be directly used just by providing event type and
    optionally definitions of event_structures which are constructed using
    EventStructuresFactory. Such created event uses default selection of
    testplans with testcases and provides only the provided event structures
    (along with possibly automatically converted event structures).

    When defining new event type, one should create a new child class
    inheriting this class providing additional methods and/or properties.
    """
    def __init__(self, event_type, **event_structures):
        self.type = event_type
        self.structures = {}
        for structure_name, fields in event_structures.items():
            self.structures[structure_name] = EventStructuresFactory.make(structure_name, fields)

    def format_branch_spec(self, fmt):
        return fmt.format(**self.structures)

    def generate_caseRunConfigurations(self, library, settings):
        """ Generates caseRunConfigurations for testcases in library relevant to this event

        :param library: Library
        :type library: tclib.Library
        :param settings: Pipeline settings
        :type settings: libpipeline.settings.Settings
        :return: CaseRunConfigurations
        :rtype: CaseRunConfigurationsList
        """
        caseruns = CaseRunConfigurationsList()

        for testplan in self.filter_testPlans(library):
            # Init testplan configurations as ConfigurationsList
            testplan_configurations = ConfigurationsList(testplan.configurations,
                                                         merge_method=settings.get('library', 'defaultCaseConfigMergeMethod'))
            for testcase in testplan.verificationTestCases:
                # Merge testplan configurations with testcase configurations
                caserun_configurations = testplan_configurations.merge(testcase.configurations)
                for configuration in caserun_configurations:
                    # Create CaseRunConfiguration
                    caseruns.append(CaseRunConfiguration(testcase, configuration, [testplan]))

        return caseruns

    def handles_testplan_artifact_type(self, artifact_type):
        """
        Decide if this event is relevant to the provided artifact_type (which
        is found in test plan).
        """
        return dotted_startswith(self.type, artifact_type)

    def filter_testPlans(self, library):
        """ Filters testplan from library based on:
        - event type and testplan.artifact_type
        - testplan execute_on filter

        :param library: pipeline library
        :type library: tclib.Library
        :return: Filtered testplans
        :rtype: list of tclib.TestPlan
        """
        return library.getTestPlansByQuery('event.handles_testplan_artifact_type(tp.artifact_type) and tp.eval_execute_on(event=event)', event=self)

    def __getattr__(self, attrname):
        if attrname not in EventStructuresFactory.known():
            return super().__getattribute__(attrname)
        try:
            return self.structures[attrname]
        except KeyError:
            pass
        structure = EventStructuresFactory.convert(attrname, self.structures)
        if structure is NotImplemented:
            # Return None if the requested structure is not compatible to
            # allow jinja templates to not crash on expressions like
            # event.nonexisting_structure.foo but to consider them as None
            return None
        self.structures[attrname] = structure
        return structure

def payload_override(payload_name):
    def decorator(method):
        @functools.wraps(method)
        def decorated(self, *args, **kwargs):
            try:
                return self.payload[payload_name]
            except KeyError:
                return method(self, *args, **kwargs)
        return decorated
    return decorator
