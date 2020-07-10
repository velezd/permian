"""
Plugins package handles organization and management (loading) of plugins.

Pipeline plugins are python packages that are placed outside of libpipeline and
symlinked in the directory of this package.

Plugins should add their functionality only via functions defined in
libpipeline.plugins.api
"""

import os
from importlib import import_module

def load():
    """Import all plugin packages."""
    plugins_path = 'plugins'
    for plugin_name in sorted(os.listdir(plugins_path)):
        if not os.path.isdir(os.path.join(plugins_path, plugin_name)):
            continue
        import_module('.'.join(['libpipeline', 'plugins', plugin_name]))
