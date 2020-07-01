"""
Plugins package handles organization and management (loading) of plugins.

Pipeline plugins are python packages that are placed outside of libpipeline and
symlinked in the directory of this package.

Plugins should add their functionality only via register functions defined
here.
"""

import os
from importlib import import_module

from ..workflows.factory import WorkflowFactory

def load():
    """Import all plugin packages."""
    plugins_path = 'plugins'
    for plugin_name in sorted(os.listdir(plugins_path)):
        if not os.path.isdir(os.path.join(plugins_path, plugin_name)):
            continue
        import_module('.'.join(['libpipeline', 'plugins', plugin_name]))


def register_workflow(name, workflow_class=None):
    """
    Redirects to WorkflowFactory.register

    Workflows define how the actual Case Runs (and their configuration) are
    executed and provide results for further processing.
    """
    return WorkflowFactory.register(name, workflow_class)


def register_provisioner(name, provisioner_class=None):
    """
    Redirects to TODO

    Provisioners provide access to external resources such as systems, services
    or files stored on remote servers.
    """


def register_reportSender(name, reportSender_class=None):
    """
    Redirects to TODO

    ReportSenders handle sending of the results to external systems such as
    email, messagebus or test case management systems. They could also provide
    locally available resutls summary files.
    """


def register_resultsProcessor(name, resultsProcessor_class=None):
    """
    Redirects to TODO

    ResultsProcessors perform transformation of results possibly adding
    additional information based on external sources such as bugzilla or change
    state of the results.
    """
