import unittest
from unittest.mock import patch, MagicMock
from . import set_jenkins_build_info
from libpipeline.settings import Settings


class ResultMock():
    @classmethod
    @property
    def status_code(cls):
        return 200
    @classmethod
    @property
    def text(cls):
        return 'OK'


requests_mock = MagicMock(return_value=ResultMock)


class TestJenkins(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.webui = MagicMock()
        cls.webui.pipeline.event = 'TestEvent'
        cls.webui.baseurl = 'http://example.com:1234/webui'

    def tearDown(self):
        requests_mock.requests_mock(return_value=ResultMock)

    @patch('requests.post', new=requests_mock)
    def test_set_build_info(self):
        self.webui.pipeline.settings = Settings(environment={}, settings_locations=[],
            cmdline_overrides={'jenkins': {'url': 'https://jenkins.example.com',
                                           'username': 'user',
                                           'password': 'pass',
                                           'job_name': 'pipeline',
                                           'build_num': '1'}})
        set_jenkins_build_info(self.webui)
        requests_mock.assert_called_with('https://jenkins.example.com/job/pipeline/1/configSubmit',
            data={'Submit': 'save',
                  'json': '{"displayName": "#1: TestEvent", "description": "WebUI: <a href=\\"http://example.com:1234/webui\\">http://example.com:1234/webui</a>"}'},
            auth=('user', 'pass'))

    @patch('requests.post', new=requests_mock)
    def test_not_set_build_info(self):
        self.webui.pipeline.settings = Settings(environment={}, settings_locations=[],
            cmdline_overrides={'jenkins': {'url': 'https://jenkins.example.com',
                                           'username': 'user',
                                           'password': 'pass',
                                           'job_name': 'pipeline',
                                           'build_num': ''}})
        set_jenkins_build_info(self.webui)
        requests_mock.assert_not_called()
