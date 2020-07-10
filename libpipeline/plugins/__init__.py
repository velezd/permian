"""
Plugins package handles organization and management (loading) of plugins.

Pipeline plugins are python packages that are placed outside of libpipeline and
symlinked in the directory of this package.

Plugins should add their functionality only via register functions defined
here.
"""

import os
from importlib import import_module

from ..events.factory import EventFactory
from ..workflows.factory import WorkflowFactory
from ..reportsenders.factory import ReportSenderFactory
from .. import hooks

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
    Redirects to ReportSenderFactory.register

    ReportSenders handle sending of the results to external systems such as
    email, messagebus or test case management systems. They could also provide
    locally available resutls summary files.
    """
    return ReportSenderFactory.register(name, reportSender_class)


def register_resultsProcessor(name, resultsProcessor_class=None):
    """
    Redirects to TODO

    ResultsProcessors perform transformation of results possibly adding
    additional information based on external sources such as bugzilla or change
    state of the results.
    """

def register_event(name, event_class=None):
    """
    Redirects to EventFactory.register

    TBD
    """
    return EventFactory.register(name, event_class)

def make_hook(name):
    """
    Redirects to hooks.define

    TBD
    """
    return hooks.define(name)

def hook_callback(hook_name):
    """
    Redirects to hooks.run_on

    TBD
    """
    return hooks.run_on(hook_name)

def hook_threaded_callback(hook_name):
    """
    Redirects to hooks.run_threaded_on

    TBD
    """
    return hooks.run_threaded_on(hook_name)
