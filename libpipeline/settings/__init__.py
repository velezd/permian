import os
import glob
import re
import collections
import configparser

from .. import plugins

DEFAULT_SETTINGS_LOCATION=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'default.ini')

class Settings():
    """
    Priority aware container for configuration options. The settings may
    be defined in following places (sorted in priority order):

     # cmdline argument
     # environment variable
     # ini file in cloned library
     # ini files in known locations (locations can be changed/added by cmdline argument or environment variable)
     # default ini files of plugins
     # default ini file of pipeline (located in libpipeline directory)

    The locations overrides are not considered to be settings and are
    treated separately.

    :param cmdline_overrides:
    :type cmdline_overrides:
    :param environment:
    :type environemnt: dict
    :param settings_locations:
    :type settings_locations: list
    :param default_settings_location: 
    :type default_settings_location: str
    """
    def __init__(self, cmdline_overrides, environment, settings_locations, default_settings_location=DEFAULT_SETTINGS_LOCATION):
        self.settings = collections.OrderedDict.fromkeys((
            'overrides',
            'environment',
            'library',
            'custom',
            'plugins',
            'default',
        ))
        for key in self.settings:
            self.settings[key] = configparser.ConfigParser()
            self.settings[key].optionxform = str # preserve case for option names

        self.settings['overrides'].read_dict(cmdline_overrides)
        self.settings['custom'].read(settings_locations)
        self.settings['default'].read(default_settings_location)
        self.settings['plugins'].read(plugins.plugin_settings())
        self.settings['environment'].read_dict(self.overrides_from_env(environment))

    def overrides_from_env(self, env, pattern_fmt=r'PIPELINE_(?P<section>[^_]+)_(?P<option>.+)'):
        """ Finds all variables in env mathing the pattern_fmt pattern
        and converts them into a dict for ConfigParser.read_dict.

        :param env: environment variables
        :type env: dict
        :param pattern_fmt: pattern for the variable name, must contain groups section and option, defaults to r'PIPELINE_(?P<section>[^_]+)_(?P<option>.+)'
        :type pattern_fmt: regexp, optional
        :return: settings found in env
        :rtype: dict
        """
        env_regex = re.compile(pattern_fmt)
        settings = dict()
        for var, value in env.items():
            match = re.match(env_regex, var)
            if match:
                if match.group('section') not in settings:
                    settings[match.group('section')] = dict()
                settings[match.group('section')][match.group('option')] = value
        return settings

    def load_from_library(self, library_path, pattern='*.ini'):
        """
        Locate all settings files in library and load them. The settings
        files are recognized by pattern and can be present in any subdirectory
        of library_path.

        :param library_path: Path where library is located
        :type library_path: str
        :param pattern: Glob pattern of files which will be considered as library settings files.
        :type pattern: str
        """
        self.settings['library'].read(glob.glob(os.path.join(library_path, pattern)))

    def get(self, section, option):
        """
        Get value of option in section taking in account priority order of
        settings sources.

        :param section: name of the section
        :type section: str
        :param option: name of the option
        :type option: str
        :return: value of option in section
        :rtype: str
        """
        for settings_source in self.settings.values():
            try:
                return settings_source[section][option]
            except KeyError:
                pass
        raise KeyError("No option '%s' defined in section '%s'" % (option, section))

    def getboolean(self, section, option):
        """
        Get value of option in section using self.get and convert it into a boolean

        :param section: name of the section
        :type section: str
        :param option: name of the option
        :type option: str
        :return: value of option in section
        :rtype: bool
        """
        for settings_source in self.settings.values():
            try:
                return settings_source.getboolean(section, option)
            except ValueError:
                raise TypeError("'Setting %s.%s=%s' is not a valid boolean - see ConfigParser.getboolean." % (section, option, settings_source[section][option]))
            except configparser.Error:
                pass
        raise KeyError("No option '%s' defined in section '%s'" % (option, section))

    def getint(self, section, option):
        """
        Get value of option in section using self.get and convert it into a int

        :param section: name of the section
        :type section: str
        :param option: name of the option
        :type option: str
        :return: value of option in section
        :rtype: bool
        """
        for settings_source in self.settings.values():
            try:
                return settings_source.getint(section, option)
            except ValueError:
                raise TypeError("'Setting %s.%s=%s' is not a valid int - see ConfigParser.getboolean." % (section, option, settings_source[section][option]))
            except configparser.Error:
                pass
        raise KeyError("No option '%s' defined in section '%s'" % (option, section))

    def getfloat(self, section, option):
        """
        Get value of option in section using self.get and convert it into a float

        :param section: name of the section
        :type section: str
        :param option: name of the option
        :type option: str
        :return: value of option in section
        :rtype: float
        """
        for settings_source in self.settings.values():
            try:
                return settings_source.getfloat(section, option)
            except ValueError:
                raise TypeError("'Setting %s.%s=%s' is not a valid float - see ConfigParser.getboolean." % (section, option, settings_source[section][option]))
            except configparser.Error:
                pass
        raise KeyError("No option '%s' defined in section '%s'" % (option, section))

    def options(self, section):
        """
        Provides all known options of the section from all settings
        files/overrides. The option may be defined in any of those sources to be
        provided by this method.

        :param section:
        :type section:
        :return: options in sections
        :rtype: set
        """
        return set([option for settings_source in self.settings.values() if settings_source.has_section(section)
                    for option in settings_source.options(section)])

    def sections(self):
        """
        Provides all known sections from all settings files/overrides. The
        section may be defined in any of those sources to be provided by this
        method.

        :return: known section
        :rtype: set
        """
        return set([section for settings_source in self.settings.values() for section in settings_source.sections()])

    def __getitem__(self, section):
        return SettingsSectionView(self, section)

class SettingsSectionView():
    """
    View on specific section of settings.

    The main purpose of this class is to provide interface for accesing settings
    values like: ``settings[section][option]`` or other dict like approaches.
    """
    def __init__(self, settings, section):
        self.settings = settings
        self.section = section

    def __getitem__(self, option):
        return self.settings.get(self.section, option)

    def __iter__(self):
        return iter(self.settings.options(self.section))
