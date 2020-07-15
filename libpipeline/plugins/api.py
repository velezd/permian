"""
TODO: Add information about possibilities to extend the pipeline. It should be categorized so that one can focus only on the area they want to extend.
In each category, provide description about which tclib data is handled by the extension (in case of Workflow, ReportSender)

Workflows:

Provisioners:

ReportSenders:

ResultsProcessors:

Input events (triggers):
Note: Mention it's good to add CLI actions associated with the event (creating the event)

CommandLine:

Web UI:

Hooks:

"""

from ..events.factory import EventFactory
from ..workflows.factory import WorkflowFactory
from ..reportsenders.factory import ReportSenderFactory
from ..cli.factory import CliFactory
from ..webui import WebUI
from .. import hooks

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

def make_hook(func):
    """
    Redirects to hooks.register.define

    TBD
    """
    return hooks.register.define(func)

def hook_callback(hook_func):
    """
    Redirects to hooks.run_on

    TBD
    """
    return hooks.register.run_on(hook_func)

def hook_threaded_callback(hook_func):
    """
    Redirects to hooks.run_threaded_on

    TBD
    """
    return hooks.register.run_threaded_on(hook_func)


def register_command_parser(name, parse_function=None):
    """
    Redirects to cli.factory.CliFactory.register_command

    TBD
    """
    return CliFactory.register_command(name, parse_function)


def register_command_args_extension(extension):
    """
    Redirects to cli.factory.CliFactory.register_argparser_extension

    TBD
    """
    return CliFactory.register_argparser_extension(extension)

def register_WebUI_blueprint(blueprint):
    """
    Redirects to webui.WebUI.registerBlueprint

    TBD
    """
    return WebUI.registerBlueprint(blueprint)
