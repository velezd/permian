import unittest
import os
import configparser
from . import Settings

class TestSettingsOverrides(unittest.TestCase):
    def test_default(self):
        # Varifies that default settings is loaded
        settings = Settings(cmdline_overrides={},
                          environment={},
                          settings_locations=[],
                          default_settings_location='./tests/test_default.ini')
        self.assertEqual(settings.get('TestSection', 'source'), 'default')

    def test_library(self):
        # Verifies that library settings overrides custom settings
        settings = Settings(cmdline_overrides={},
                          environment={},
                          settings_locations=['./tests/test_settings.ini'])
        settings.load_from_library('./tests/test_library')
        self.assertEqual(settings.get('TestSection', 'source'), 'library')

    def test_environment(self):
        # Verifies that environment settings overrides library settings
        settings = Settings(cmdline_overrides={},
                          environment={'PIPELINE_TestSection_source': "env"},
                          settings_locations=[])
        settings.load_from_library('./tests/test_library')
        self.assertEqual(settings.get('TestSection', 'source'), 'env')

    def test_cmdline(self):
        # Verifies that cmdline settings overrides environment settings
        settings = Settings(cmdline_overrides={'TestSection': {'source': 'cmdline'}},
                          environment={},
                          settings_locations=[])
        self.assertEqual(settings.get('TestSection', 'source'), 'cmdline')

class TestSettingsOverridesPlugin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.mkdir('./libpipeline/plugins/testplugin')
        with open('./libpipeline/plugins/testplugin/settings.ini', 'w') as settings_file:
            settings_file.write('[TestSection]\nsource=plugin')

    @classmethod
    def tearDownClass(cls):
        os.unlink('./libpipeline/plugins/testplugin/settings.ini')
        os.rmdir('./libpipeline/plugins/testplugin')

    def test_plugins(self):
        # Verifies that plugin settings overrides default settings
        settings = Settings(cmdline_overrides={},
                          environment={},
                          settings_locations=[],
                          default_settings_location='./tests/test_default.ini')
        self.assertEqual(settings.get('TestSection', 'source'), 'plugin')

    def test_custom(self):
        # Verifies that custom settings overrides plugin settings
        settings = Settings(cmdline_overrides={},
                          environment={},
                          settings_locations=['./tests/test_settings.ini'])
        self.assertEqual(settings.get('TestSection', 'source'), 'custom')

class TestSettingsDefault(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_parser = configparser.ConfigParser()
        cls.test_parser.optionxform = str # preserve case for option names
        cls.test_parser.read('./libpipeline/default.ini')

    def test_real_default(self):
        settings = Settings(cmdline_overrides={},
                          environment={},
                          settings_locations=[])
        self.assertDictEqual(self.test_parser._sections, settings.settings['default']._sections)

class TestSettingsListing(unittest.TestCase):
    def test_sections(self):
        settings = Settings(cmdline_overrides={},
                          environment={},
                          settings_locations=[],
                          default_settings_location='./tests/test_default.ini')
        self.assertTrue('TestSection' in settings.sections())

    def test_options(self):
        settings = Settings(cmdline_overrides={},
                          environment={},
                          settings_locations=[],
                          default_settings_location='./tests/test_default.ini')
        self.assertEqual(settings.options('TestSection'), {'source'})
