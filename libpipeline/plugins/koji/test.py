import unittest
import re
from unittest.mock import patch, create_autospec
import productmd

from libpipeline.events.factory import EventFactory
from libpipeline.cli.factory import CliFactory

from . import KojiEvent, KojiBuild

@patch('xmlrpc.client.ServerProxy')
class TestKojiEvent(unittest.TestCase):
    hub_url = 'http://koji.example.com/path/to/hub'
    nvr = 'foo-1.2-3.dt4'
    tag = 'bar'

    def test_minimal(self, koji_proxy_class):
        event = EventFactory.make(
            None,
            CliFactory.parse('koji_build_tag', [self.hub_url, self.nvr, self.tag])[1]
        )
        self.assertIsInstance(event, KojiEvent)
        self.assertIsInstance(event.koji_build, KojiBuild)
        self.assertEqual(event.koji_build.nvr, self.nvr)
        self.assertEqual(event.koji_build.new_tag, self.tag)
        self.assertEqual(event.type, 'koji.build.tag')

    def test_all(self, koji_proxy_class):
        event_type = 'koji.hello'
        build_id = 67890
        task_id = 12345
        package_name = 'stress-o-meter'
        command_args = [
            self.hub_url,
            self.nvr,
            self.tag,
            '--event-type', event_type,
            '--build-id', str(build_id),
            '--task-id', str(task_id),
            '--package-name', package_name,
        ]
        event = EventFactory.make(
            None,
            CliFactory.parse('koji_build_tag', command_args)[1]
        )
        self.assertIsInstance(event, KojiEvent)
        self.assertIsInstance(event.koji_build, KojiBuild)
        self.assertEqual(event.koji_build.nvr, self.nvr)
        self.assertEqual(event.koji_build.new_tag, self.tag)
        self.assertEqual(event.type, event_type)
        self.assertEqual(event.koji_build.build_id, build_id)
        self.assertEqual(event.koji_build.task_id, task_id)
        self.assertEqual(event.koji_build.package_name, package_name)
        self.assertEqual(str(event), f'stress-o-meter {self.nvr} {self.tag}')

@patch('xmlrpc.client.ServerProxy')
class TestKojiEventStructure(unittest.TestCase):
    hub_url = 'http://koji.example.com/path/to/hub'
    nvr = 'foo-1.2-3.dt4'
    build_id = 1001
    task_id = 1337
    package_name = 'surprise!'
    new_tag = 'acme-1.2.3-poof'
    composes_baseurl = 'http://example.com/composes/foo'

    def test_minimal(self, koji_proxy_class):
        koji_build = KojiBuild(None, self.hub_url, self.nvr)
        self.assertEqual(koji_build.hub_url, self.hub_url)
        self.assertEqual(koji_build.nvr, self.nvr)

    def test_discovery(self, koji_proxy_class):
        koji_proxy_class.return_value.getBuild.return_value = {
            'build_id' : self.build_id,
            'task_id' : self.task_id,
            'package_name' : self.package_name,
        }
        koji_proxy_class.return_value.listTags.return_value = (
            {'name': self.new_tag},
            {'name': 'foo'},
        )
        koji_build = KojiBuild(None, self.hub_url, self.nvr)
        self.assertEqual(koji_build.hub_url, self.hub_url)
        self.assertEqual(koji_build.nvr, self.nvr)
        self.assertEqual(koji_build.build_id, self.build_id)
        self.assertEqual(koji_build.task_id, self.task_id)
        self.assertEqual(koji_build.package_name, self.package_name)
        self.assertEqual(koji_build.new_tag, self.new_tag)
        koji_proxy_class.assert_called_with(self.hub_url, allow_none=True)
        koji_proxy_class.return_value.getBuild.assert_called_once_with(self.nvr, True)
        koji_proxy_class.return_value.listTags.assert_called_once_with(self.build_id, None, False)

    def test_all(self, koji_proxy_class):
        koji_build = KojiBuild(
            None,
            self.hub_url, self.nvr, build_id=self.build_id,
            task_id=self.task_id, package_name=self.package_name,
            new_tag=self.new_tag
        )
        self.assertEqual(koji_build.nvr, self.nvr)
        self.assertEqual(koji_build.build_id, self.build_id)
        self.assertEqual(koji_build.task_id, self.task_id)
        self.assertEqual(koji_build.package_name, self.package_name)
        self.assertEqual(koji_build.new_tag, self.new_tag)
        koji_proxy_class.assert_not_called()
        koji_proxy_class.return_value.getBuild.assert_not_called()

    @patch('requests.get')
    @patch('productmd.compose.Compose')
    def test_convert_compose(self, Compose, requests_get, koji_proxy_class):
        compose_id = 'FooBar-1.23-123456.t.98'
        compose_relpath = '../some_compose_dir'
        koji_proxy_class.return_value.getBuild.return_value = {
            'build_id' : self.build_id,
            'task_id' : self.task_id,
            'package_name' : self.package_name,
        }
        koji_proxy_class.return_value.listTags.return_value = (
            {'name': self.new_tag},
        )
        Compose.return_value.info.compose.id = compose_id
        requests_get.return_value.text = compose_relpath
        koji_build = KojiBuild(None, self.hub_url, self.nvr, composes_baseurl=self.composes_baseurl)
        compose = koji_build.to_compose()
        self.assertEqual(compose.id, compose_id)
        self.assertEqual(
            compose.location,
            f'{self.composes_baseurl}/{compose_relpath}'
        )
