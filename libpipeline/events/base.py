import functools
from ..caserunconfiguration import CaseRunConfiguration, ConfigurationsList, CaseRunConfigurationsList
from tclib.expressions import eval_bool
#from ..exceptions import UnknownEventSubTypeExpression

class Event():
    """
    Base class of event which takes the event payload and stores it in payload
    property. The type is stored in the type property.
    """
    def __init__(self, event_type, payload, other_data):
        self.type = event_type
        self.payload = self.process_payload(payload)
        self.other_data = other_data

    def process_payload(self, payload):
        return payload

    def format_branch_spec(self, fmt):
        return fmt.format(**self.payload)

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

    def filter_testPlans(self, library):
        """ Filters testplan from library based on:
        - event type and testplan.artifact_type
        - testplan execute_on filter

        :param library: pipeline library
        :type library: tclib.Library
        :return: Filtered testplans
        :rtype: list of tclib.TestPlan
        """
        return library.getTestPlansByQuery('tp.artifact_type == event.type and tp.eval_execute_on(event=event)', event=self)


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
