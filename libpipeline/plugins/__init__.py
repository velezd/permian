"""
Plugins package handles organization and management (loading) of plugins.

Pipeline plugins are python packages that are placed outside of libpipeline and
symlinked in the directory of this package.

Plugins should add their functionality only via functions defined in
libpipeline.plugins.api
"""

import logging
import os
from importlib import import_module

from . import api

PLUGINS_PATH = os.path.dirname(os.path.abspath(__file__))

def load():
    """Import all plugin packages."""
    for plugin_name in sorted(os.listdir(PLUGINS_PATH)):
        if not os.path.isdir(os.path.join(PLUGINS_PATH, plugin_name)):
            continue
        import_module('.'.join(['libpipeline', 'plugins', plugin_name]))

def plugin_settings():
    """ Get paths for plugin settings files """
    for plugin_name in sorted(os.listdir(PLUGINS_PATH)):
        plugin_settings = os.path.join(PLUGINS_PATH, plugin_name, 'settings.ini')
        if os.path.exists(plugin_settings):
            yield plugin_settings
