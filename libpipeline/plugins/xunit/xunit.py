import abc
import jinja2
from ...reportsenders.base import BaseReportSender


def filter_results_string(crcs_list):
    """ Jijna2 filter - takes individual results of configurations and creates one human readable string from them.

    :param crcs_list: list of CaseRunConfiguration
    :type crcs_list: list
    :return: String with results
    :rtype: str
    """
    string = ''
    base_string = 'Configuration: %s - Result: %s, %s - Links: %s; '
    for caserun in crcs_list:
        string += base_string % (str(caserun.configuration),
                                 str(caserun.result.state),
                                 str(caserun.result.result),
                                 ', '.join([ link for link in caserun.result.extra_fields.get('beaker_links', ['None']) ]))
    return string


class BaseXunitReportSender(BaseReportSender):
    """ Base xunit report sender, should not be used by itself - only as a parent class for other report senders. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.env = jinja2.Environment(loader=jinja2.PackageLoader('libpipeline.plugins.xunit', '.'),
                                      autoescape=True)
        self.env.filters.update({'results_string': filter_results_string})
        self.template = self.env.get_template('xunit.xml.j2')

        # Maps testcase result to a result reported in xunit
        self.results_map = {None: 'skipped',
                            'FAIL': 'failure',
                            'ERROR': 'error'}

    def generate(self, properties={}):
        """ Generates xunit xml from caseRunConfigurations, xunit template and optional properties

        :param properties: Example: {None: {'polarion-project-id': 'TestingProject'}, 'testcase 1': {'polarion-testcase-id': 'TEST-1234'}}, defaults to {}
        :type properties: dict, optional
        :return: xunit xml
        :rtype: str
        """
        return self.template.render(testcases=self.caseRunConfigurations.by_testcase(),
                                    reportsender=self,
                                    properties=properties)
