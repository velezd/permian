import unittest
from unittest.mock import patch, MagicMock, call
from . import env_plugins_override, disabled, load
from importlib import import_module
import importlib

mocked_os_environ = {'SOMETHING_ELSE': 'foo',
                     'PIPELINEPLUGINS_DISABLE': 'plugin1,plugin2,plugin3',
                     'PIPELINEPLUGINS_ENABLE': 'plugin4'}

mock = MagicMock()

TEST_PLUGINS_PATH = 'tests/plugins'

class TestPluginsOverride(unittest.TestCase):
    @patch('os.environ', new=mocked_os_environ)
    def test_env_plugins_override(self):
        disabled, enabled = env_plugins_override()
        self.assertEqual(disabled, {'plugin1', 'plugin2', 'plugin3'})
        self.assertEqual(enabled, {'plugin4'})

    @patch('libpipeline.plugins.PLUGINS_PATH', new=TEST_PLUGINS_PATH)
    def test_plugins_disabled_flag(self):
        self.assertFalse(disabled('test1_enabled'))
        self.assertTrue(disabled('test2_disabled'))

    @patch('libpipeline.plugins.DISABLED_PLUGINS', new={'test1_enabled'})
    @patch('libpipeline.plugins.ENABLED_PLUGINS', new={'test2_disabled'})
    @patch('libpipeline.plugins.PLUGINS_PATH', new=TEST_PLUGINS_PATH)
    def test_plugins_disabled_override(self):
        self.assertTrue(disabled('test1_enabled'))
        self.assertFalse(disabled('test2_disabled'))

class TestPluginsLoad(unittest.TestCase):
    @patch('importlib.import_module', new=mock)
    @patch('libpipeline.plugins.PLUGINS_PATH', new=TEST_PLUGINS_PATH)
    def test_plugins_load(self):
        self.assertEqual([], mock.call_args_list)
        load()
        self.assertTrue(call('libpipeline.plugins.test1_enabled') in mock.call_args_list)
        self.assertFalse(call('libpipleine.plugins.test2_disabled') in mock.call_args_list)

 