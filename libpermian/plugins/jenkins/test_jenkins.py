import unittest
from unittest.mock import patch, MagicMock

from . import set_jenkins_build_info, set_jenkins_build_info_static_webui
from libpermian.settings import Settings


class ResultMock():
    @classmethod
    @property
    def status_code(cls):
        return 200
    @classmethod
    @property
    def text(cls):
        return 'OK'


class TestJenkins(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.webui = MagicMock()
        cls.webui.pipeline.event = 'TestEvent'
        cls.webui.baseurl = 'http://example.com:1234/webui'

    @patch('requests.post')
    def test_set_build_info(self, requests_post):
        requests_post.return_value = ResultMock()
        self.webui.pipeline.settings = Settings(environment={}, settings_locations=[],
            cmdline_overrides={'jenkins': {'url': 'https://jenkins.example.com',
                                           'username': 'user',
                                           'password': 'pass',
                                           'job_name': 'pipeline',
                                           'build_num': '1'}})
        set_jenkins_build_info(self.webui)
        requests_post.assert_called_with('https://jenkins.example.com/job/pipeline/1/configSubmit',
            data={'Submit': 'save',
                  'json': '{"displayName": "#1: TestEvent", "description": "<a href=\\"http://example.com:1234/webui\\">WebUI</a>"}'},
            auth=('user', 'pass'))

    @patch('requests.post')
    def test_not_set_build_info(self, requests_post):
        requests_post.return_value = ResultMock()
        self.webui.pipeline.settings = Settings(environment={}, settings_locations=[],
            cmdline_overrides={'jenkins': {'url': 'https://jenkins.example.com',
                                           'username': 'user',
                                           'password': 'pass',
                                           'job_name': 'pipeline',
                                           'build_num': ''}})
        set_jenkins_build_info(self.webui)
        requests_post.assert_not_called()

    @patch('requests.post')
    def test_set_static_webui_build_info(self, requests_post):
        requests_post.return_value = ResultMock()
        self.webui.pipeline.settings = Settings(environment={}, settings_locations=[],
            cmdline_overrides={'jenkins': {'url': 'https://jenkins.example.com',
                                           'username': 'user',
                                           'password': 'pass',
                                           'job_name': 'pipeline',
                                           'build_num': '1'}})
        set_jenkins_build_info_static_webui(self.webui.pipeline, './some/path/file.suffix')
        requests_post.assert_called_with('https://jenkins.example.com/job/pipeline/1/configSubmit',
            data={'Submit': 'save',
                  'json': '{"displayName": "#1: TestEvent", "description": "<a href=\\"https://jenkins.example.com/job/pipeline/1/artifact/./some/path/file.suffix\\">WebUI</a>"}'},
            auth=('user', 'pass'))

    @patch('requests.post')
    def test_not_set_static_webui_build_info(self, requests_post):
        self.webui.pipeline.settings = Settings(environment={}, settings_locations=[],
            cmdline_overrides={'jenkins': {'url': 'https://jenkins.example.com',
                                           'username': 'user',
                                           'password': 'pass',
                                           'job_name': 'pipeline',
                                           'build_num': ''}})
        set_jenkins_build_info_static_webui(self.webui.pipeline, './some/path/file.suffix')
        requests_post.assert_not_called()
