import abc
import jinja2
from ...reportsenders.base import BaseReportSender


class BaseXunitReportSender(BaseReportSender):
    """ Base xunit report sender, should not be used by itself - only as a parent class for other report senders. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.env = jinja2.Environment(loader=jinja2.PackageLoader('libpermian.plugins.xunit', '.'),
                                      autoescape=True)
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

    def xunitResultOf(self, caseRunConfigurations):
        return self.results_map.get(self.resultOf(caseRunConfigurations))
