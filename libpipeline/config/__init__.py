import os
import glob
import re
import collections
import configparser

from .. import plugins

DEFAULT_CONFIG_LOCATION=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'default.ini')

class Config():
    """
    Priority aware container for configuration options. The configuration may
    be defined in following places (sorted in priority order):

     # cmdline argument
     # environment variable
     # ini file in cloned library
     # ini files in known locations (locations can be changed/added by cmdline argument or environment variable)
     # default ini files of plugins
     # default ini file of pipeline (located in config directory in libpipeline)

    The locations overrides are not considered to be configuration and are
    treated separately.

    :param cmdline_overrides:
    :type cmdline_overrides:
    :param environment:
    :type environemnt: dict
    :param config_locations:
    :type config_locations: list
    :param default_config_location: 
    :type default_config_location: str
    """
    def __init__(self, cmdline_overrides, environment, configs_locations, default_config_location=DEFAULT_CONFIG_LOCATION):
        self.configs = collections.OrderedDict.fromkeys((
            'overrides',
            'environment',
            'library',
            'custom',
            'plugins',
            'default',
        ))
        for key in self.configs:
            self.configs[key] = configparser.ConfigParser()

        self.configs['overrides'].read_dict(cmdline_overrides)
        self.configs['custom'].read(configs_locations)
        self.configs['default'].read(default_config_location)
        self.configs['plugins'].read(plugins.plugin_configurations())
        self.configs['environment'].read_dict(self.overrides_from_env(environment))

    def overrides_from_env(self, env, pattern_fmt=r'PIPELINE_(?P<section>[^_]+)_(?P<option>.+)'):
        """ Finds all variables in env mathing the pattern_fmt pattern
        and converts them into a dict for ConfigParser.read_dict.

        :param env: environment variables
        :type env: dict
        :param pattern_fmt: pattern for the variable name, must contain groups section and option, defaults to r'PIPELINE_(?P<section>[^_]+)_(?P<option>.+)'
        :type pattern_fmt: regexp, optional
        :return: configuration found in env
        :rtype: dict
        """
        env_regex = re.compile(pattern_fmt)
        config = dict()
        for var, value in env.items():
            match = re.match(env_regex, var)
            if match:
                if match.group('section') not in config:
                    config[match.group('section')] = dict()
                config[match.group('section')][match.group('option')] = value
        return config

    def load_from_library(self, library_path, pattern='*.ini'):
        """
        Locate all configuration files in library and load them. The config
        files are recognized by pattern and can be present in any subdirectory
        of library_path.

        :param library_path: Path where library is located
        :type library_path: str
        :param pattern: Glob pattern of files which will be considered as library config files.
        :type pattern: str
        """
        self.configs['library'].read(glob.glob(os.path.join(library_path, pattern)))

    def get(self, section, option):
        """
        Get value of option in section taking in account priority order of
        config sources.

        :param section:
        :type section:
        :param option:
        :type option:
        :return: value of option in section
        :rtype: str
        """
        for config in self.configs.values():
            try:
                return config[section][option]
            except KeyError:
                pass
        raise KeyError("No option '%s' defined in section '%s'" % (option, section))

    def options(self, section):
        """
        Provides all known options of the section from all config
        files/overrides. The option may be defined in any of those sources to be
        provided by this method.

        :param section:
        :type section:
        :return: options in sections
        :rtype: set
        """
        return set([ option for config in self.configs.values() if config.has_section(section)
                            for option in config.options(section) ])

    def sections(self):
        """
        Provides all known sections from all config files/overrides. The
        section may be defined in any of those sources to be provided by this
        method.

        :return: known section
        :rtype: set
        """
        return set([ section for config in self.configs.values() for section in config.sections() ])

    def __getitem__(self, section):
        return ConfigSectionView(self, section)

class ConfigSectionView():
    """
    View on specific section of Config.

    The main purpose of this class is to provide interface for accesing config
    values like: ``config[section][option]`` or other dict like approaches.
    """
    def __init__(self, config, section):
        self.config = config
        self.section = section

    def __getitem__(self, option):
        return self.config.get(self.section, option)

    def __iter__(self):
        return iter(self.config.options(self.section))
