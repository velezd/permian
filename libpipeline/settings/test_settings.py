import unittest
import os
import configparser
import shutil
from . import Settings
from libpipeline.plugins import load

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
        with open('./libpipeline/plugins/testplugin/__init__.py', 'w') as init_file:
            pass
        with open('./libpipeline/plugins/testplugin/settings.ini', 'w') as settings_file:
            settings_file.write('[TestSection]\nsource=plugin')
        load()  # Reload plugins

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree('./libpipeline/plugins/testplugin')

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
        self.assertEqual(settings.options('TestSection'), {'source', 'optionA'})

class TestSettingsMerge(unittest.TestCase):
    def test_sections(self):
        settings = Settings(cmdline_overrides={},
                          environment={},
                          settings_locations=['./tests/test_settings.ini'],
                          default_settings_location='./tests/test_default.ini')
        self.assertTrue('TestSection' in settings.sections())

    def test_options(self):
        settings = Settings(cmdline_overrides={},
                          environment={},
                          settings_locations=['./tests/test_settings.ini'],
                          default_settings_location='./tests/test_default.ini')
        self.assertEqual(settings.options('TestSection'), {'source', 'optionA', 'optionB'})

    def test_values(self):
        settings = Settings(cmdline_overrides={},
                          environment={},
                          settings_locations=['./tests/test_settings.ini'],
                          default_settings_location='./tests/test_default.ini')
        self.assertCountEqual(
            [
                (option, settings.get('TestSection', option))
                for option in settings.options('TestSection')
            ],
            [
                ('source', 'custom'),
                ('optionA', 'defaultA'),
                ('optionB', 'settingsB'),
            ]
        )

class TestSettingsSectionFallback(unittest.TestCase):
    def setUp(self):
        self.settings = Settings(
            cmdline_overrides={
                'primary' : {
                    'common' : 'CommonPrimaryValue',
                    'only_primary': 'OnlyPrimaryValue',
                },
                'secondary' : {
                    'common' : 'CommonSecondaryValue',
                    'nonprimary' : 'NonprimarySecondaryValue',
                    'only_secondary': 'OnlySecondaryValue',
                },
                'tertiary' : {
                    'common' : 'CommonTertiaryValue',
                    'nonprimary' : 'NonprimaryTertiaryValue',
                    'only_tertiary': 'OnlyTertiaryValue',
                },
            },
            environment={},
            settings_locations=[],
        )
        self.sections = ('primary', 'secondary', 'tertiary')

    def testFallback(self):
        self.assertEqual(
            self.settings.get(self.sections, 'common'),
            self.settings.get('primary', 'common'),
        )
        self.assertEqual(
            self.settings.get(self.sections, 'nonprimary'),
            self.settings.get('secondary', 'nonprimary'),
        )
        self.assertEqual(
            self.settings.get(self.sections, 'only_primary'),
            self.settings.get('primary', 'only_primary'),
        )
        self.assertEqual(
            self.settings.get(self.sections, 'only_secondary'),
            self.settings.get('secondary', 'only_secondary'),
        )
        self.assertEqual(
            self.settings.get(self.sections, 'only_tertiary'),
            self.settings.get('tertiary', 'only_tertiary'),
        )
