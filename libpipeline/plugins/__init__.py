"""
Plugins package handles organization and management (loading) of plugins.

Pipeline plugins are python packages that are placed outside of libpipeline and
symlinked in the directory of this package.

Plugins should add their functionality only via functions defined in
libpipeline.plugins.api
"""

import logging
import os
import importlib

from . import api


def env_plugins_override():
    """ Get enabled and disabled plugin names from env variables

    :return: DISABLED_PLUGINS, ENABLED_PLUGINS
    :rtype: tuple
    """
    disable = os.environ.get('PIPELINEPLUGINS_DISABLE', '')
    disable = set(disable.split(',')) if disable != '' else set()
    enable = os.environ.get('PIPELINEPLUGINS_ENABLE', '')
    enable = set(enable.split(',')) if enable != '' else set()

    if disable.intersection(enable):
        raise RuntimeError('Plugin cannot be enabled and disabled at the same time, check env.')

    return disable, enable


PLUGINS_PATH = os.path.dirname(os.path.abspath(__file__))
DISABLED_PLUGINS, ENABLED_PLUGINS = env_plugins_override()


def disabled(plugin_name):
    """ Checks if plugin is disabled """
    if  os.path.exists(os.path.join(PLUGINS_PATH, plugin_name, 'DISABLED')) and plugin_name not in ENABLED_PLUGINS:
        return True
    if plugin_name in DISABLED_PLUGINS:
        return True
    return False

def load():
    """Import all plugin packages."""
    for plugin_name in sorted(os.listdir(PLUGINS_PATH)):
        # TODO: Add logger to log what plugins are (not) loaded and why
        if not os.path.isdir(os.path.join(PLUGINS_PATH, plugin_name)):
            continue
        if disabled(plugin_name):
            continue
        importlib.import_module('.'.join(['libpipeline', 'plugins', plugin_name]))

def plugin_settings():
    """ Get paths for plugin settings files """
    for plugin_name in sorted(os.listdir(PLUGINS_PATH)):
        if disabled(plugin_name):
            continue
        plugin_settings = os.path.join(PLUGINS_PATH, plugin_name, 'settings.ini')
        if os.path.exists(plugin_settings):
            yield plugin_settings
