import abc
import jinja2
from ...testruns import merge_testcase_configurations
from ...reportsenders.base import BaseReportSender


class BaseXunitReportSender(BaseReportSender):
    """ Base xunit report sender, should not be used by itself - only as a parent class for other report senders. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.env = jinja2.Environment(loader=jinja2.PackageLoader('libpipeline.plugins.xunit', '.'),
                                      autoescape=True)
        self.template = self.env.get_template('xunit.xml.j2')

    def generate(self, properties={}):
        """ Generates xunit xml from caseRunConfigurations, xunit template and optional properties

        :param properties: Example: {None: {'polarion-project-id': 'TestingProject'}, 'testcase 1': {'polarion-testcase-id': 'TEST-1234'}}, defaults to {}
        :type properties: dict, optional
        :return: xunit xml
        :rtype: str
        """
        return self.template.render(testcases=merge_testcase_configurations(self.caseRunConfigurations),
                                    reportsender=self,
                                    properties=properties)
