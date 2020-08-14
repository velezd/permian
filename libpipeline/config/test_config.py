import unittest
import os
import configparser
from . import Config

class TestConfigOverrides(unittest.TestCase):
    def test_default(self):
        # Varifies that default config is loaded
        config = Config(cmdline_overrides={},
                        environment={},
                        configs_locations=[],
                        default_config_location='./tests/test_default.ini')
        self.assertEqual(config.get('TestSection', 'source'), 'default')

    def test_library(self):
        # Verifies that library config overrides custom config
        config = Config(cmdline_overrides={},
                        environment={},
                        configs_locations=['./tests/test_config.ini'])
        config.load_from_library('./tests/test_library')
        self.assertEqual(config.get('TestSection', 'source'), 'library')

    def test_environment(self):
        # Verifies that environment config overrides library config
        config = Config(cmdline_overrides={},
                        environment={'PIPELINE_TestSection_source': "env"},
                        configs_locations=[])
        config.load_from_library('./tests/test_library')
        self.assertEqual(config.get('TestSection', 'source'), 'env')

    def test_cmdline(self):
        # Verifies that cmdline config overrides environment config
        config = Config(cmdline_overrides={'TestSection': {'source': 'cmdline'}},
                        environment={},
                        configs_locations=[])
        self.assertEqual(config.get('TestSection', 'source'), 'cmdline')

class TestConfigOverridesPlugin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.mkdir('./libpipeline/plugins/testplugin')
        with open('./libpipeline/plugins/testplugin/config.ini', 'w') as configfile:
            configfile.write('[TestSection]\nsource=plugin')

    @classmethod
    def tearDownClass(cls):
        os.unlink('./libpipeline/plugins/testplugin/config.ini')
        os.rmdir('./libpipeline/plugins/testplugin')

    def test_plugins(self):
        # Verifies that plugin config overrides default config
        config = Config(cmdline_overrides={},
                        environment={},
                        configs_locations=[],
                        default_config_location='./tests/test_default.ini')
        self.assertEqual(config.get('TestSection', 'source'), 'plugin')

    def test_custom(self):
        # Verifies that custom config overrides plugin config
        config = Config(cmdline_overrides={},
                        environment={},
                        configs_locations=['./tests/test_config.ini'])
        self.assertEqual(config.get('TestSection', 'source'), 'custom')

class TestConfigDefault(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_parser = configparser.ConfigParser()
        cls.test_parser.read('./libpipeline/default.ini')

    def test_real_default(self):
        config = Config(cmdline_overrides={},
                        environment={},
                        configs_locations=[])
        self.assertDictEqual(self.test_parser._sections, config.configs['default']._sections)

class TestConfigListing(unittest.TestCase):
    def test_sections(self):
        config = Config(cmdline_overrides={},
                        environment={},
                        configs_locations=[],
                        default_config_location='./tests/test_default.ini')
        self.assertEqual(config.sections(), {'TestSection'})

    def test_options(self):
        config = Config(cmdline_overrides={},
                        environment={},
                        configs_locations=[],
                        default_config_location='./tests/test_default.ini')
        self.assertEqual(config.options('TestSection'), {'source'})
