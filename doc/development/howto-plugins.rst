==================
Plugin development
==================

Overview
========

Permian uses a plugin-based architecture that allows you to extend its functionality without modifying the core codebase. Plugins are Python packages that register components through a well-defined API.

Plugin Structure
================

Basic Layout
------------

A plugin is a Python package located in ``libpermian/plugins/`` with the following structure::

    libpermian/plugins/
    └── myplugin/
        ├── __init__.py          # Required: Plugin registration code
        ├── settings.ini         # Optional: Plugin-specific settings
        └── [other modules]      # Optional: Additional plugin code

Plugin Loading
--------------

Plugins are automatically discovered and loaded when:

1. They are located in the ``libpermian/plugins/`` directory or path defined in ``PIPELINEPLUGINS_PATH``
2. They contain an ``__init__.py`` file
3. They are not disabled via ``DISABLED`` file or environment variables.

   Create a ``DISABLED`` file in the plugin directory if you want to disable it by default::

    touch libpermian/plugins/myplugin/DISABLED

**Environment Variables:**

- ``PIPELINEPLUGINS_DISABLE`` - Comma-separated list of plugin names to disable
- ``PIPELINEPLUGINS_ENABLE`` - Comma-separated list of plugin names to enable (overrides DISABLED file)
- ``PIPELINEPLUGINS_PATH`` - Colon-separated paths to additional plugin directories

Plugin API
==========

The plugin API is exposed through ``libpermian.plugins.api`` and provides several extension points:

Events
------

Register custom event types that trigger pipeline execution.

**Register Event Type:**

.. code-block:: python

    from libpermian.plugins import api
    from libpermian.events.base import Event

    @api.events.register('myevent')
    class MyEvent(Event):
        def __init__(self, settings, type, **kwargs):
            super().__init__(settings, type, **kwargs)

        def __str__(self):
            return 'MyEvent'

**Register Event Structure:**

Register event structures, they provide additional information related to the event

The structure classes can define special `from_*` classmethods and
`to_*` methods which can be used for conversions either from another
structure or to another structure where the asterisk represents name
under which is the other structure class registered.

.. code-block:: python

    from libpermian.events.structures.base import BaseStructure

    @api.events.register_structure('mystructure')
    class MyStructure(BaseStructure):
        def __init__(self, settings, field1, field2=None):
            super().__init__(settings)
            self.field1 = field1
            self.field2 = field2

Workflows
---------

Register workflows that define how test cases are executed.

.. code-block:: python

    from libpermian.workflows.isolated import IsolatedWorkflow
    from libpermian.result import Result

    @api.workflows.register("myworkflow")
    class MyWorkflow(IsolatedWorkflow):
        def setup(self):
            """Executed before execute(). Use for preparation tasks."""
            self.reportResult(Result('queued'))

        def execute(self):
            """Contains the main test execution logic. Required."""
            self.reportResult(Result('started'))
            # Your test logic here
            self.log('Log message', 'logfile')
            self.addLog('local.txt', '/path/to/file')

        def teardown(self):
            """Executed after execute(). Use for cleanup."""
            self.reportResult(Result('complete', 'PASS', final=True))

        def terminate(self):
            """Called asynchronously to stop execution."""
            return False

        def displayStatus(self):
            """Return status string for WebUI display."""
            return 'Running my workflow'

**Grouped Workflows:**

For workflows that handle multiple test case runs together:

.. code-block:: python

    from libpermian.workflows.isolated import GroupedWorkflow

    @api.workflows.register("grouped_workflow")
    class MyGroupedWorkflow(GroupedWorkflow):
        @classmethod
        def factory(cls, testRuns, crcList):
            """Create instances grouping CRCs as needed."""
            for testcase, crcs in crcList.by_testcase():
                cls(testRuns, crcs)

        def execute(self):
            # Use groupReportResult, groupLog, groupAddLog methods
            self.groupReportResult(self.crcList, Result('started'))

Report Senders
--------------

Register report senders that handle results reporting to external systems.

.. code-block:: python

    from libpermian.reportsenders.base import BaseReportSender

    @api.reportsenders.register('myreporter')
    class MyReportSender(BaseReportSender):
        def processPartialResult(self, result):
            """Handle interim results."""
            pass

        def processFinalResult(self, result):
            """Handle final test results."""
            pass

        def processTestRunStarted(self):
            """Called when test run starts."""
            pass

        def processTestRunFinished(self):
            """Called when test run finishes."""
            pass

        def processCaseRunFinished(self, testCaseID):
            """Called when a test case run completes."""
            pass

CLI Commands
------------

Register custom CLI commands and arguments.

**Register Command Parser:**

.. code-block:: python

    import json
    from libpermian.cli.parser import ToPayload

    @api.cli.register_command_parser('mycommand')
    def mycommand_parser(base_parser, args):
        parser = base_parser
        parser.add_argument('id', action=ToPayload,
                            help='Resource ID')
        parser.add_argument('--option', action=ToPayload,
                            help='Optional parameter')
        options = parser.parse_args(args)
        return options, json.dumps({
            'type': options.event_type or 'myevent',
            'mystructure': options.payload
        })

**Extend Global Arguments:**

.. code-block:: python

    @api.cli.register_command_args_extension
    def extend_args(parser):
        parser.add_argument('--my-global-arg', action='store_true')
        return parser

Hooks
-----

Define and respond to custom hooks for event-driven behavior.

.. code-block:: python

    # Define a hook
    @api.hooks.make
    def my_hook(data):
        pass

    # Register synchronous callback
    @api.hooks.callback_on(my_hook)
    def handle_my_hook(data):
        # Process the hook
        pass

    # Register threaded callback (runs in background)
    @api.hooks.threaded_callback_on(my_hook)
    def handle_my_hook_async(data):
        # Process the hook asynchronously
        pass

    # Trigger the hook
    my_hook('some data')

Web UI
------

Register Flask blueprints to add custom web UI pages.

.. code-block:: python

    from flask import Blueprint

    my_blueprint = Blueprint('myplugin', __name__)

    @my_blueprint.route('/mypage')
    def my_page():
        return 'Hello from my plugin!'

    @api.webui.register_blueprint(my_blueprint, url_prefix='/myplugin')

Issue Analyzer
--------------

Register issue analyzers for test failure analysis.

.. code-block:: python

    @api.issueanalyzer.register
    class MyAnalyzer:
        # Implementation details
        pass

Plugin Settings
===============

Plugins can provide default settings via ``settings.ini`` file in the plugin directory:

.. code-block:: ini

    [mysection]
    option1 = value1
    option2 = value2

Settings can be accessed through the ``settings`` object passed to plugin components.

Best Practices
==============

1. **Naming**: Use descriptive, unique names for your plugin and registered components
2. **Dependencies**: Import from ``libpermian.plugins import api`` at the module level
3. **Error Handling**: Properly handle exceptions and provide meaningful error messages
4. **Logging**: Use the standard Python logging module for debugging
5. **Documentation**: Document your plugin's purpose, configuration options, and usage. This should be done as docstrings in the code.
6. **Testing**: Write unit tests for your plugin in a ``test_*.py`` file

Example
-------
See a complete working example in ``libpermian/plugins/example/__init__.py`` which should demonstrates basic plugin API features.

The ``compose`` plugin is a good example of real Event and Event structure

API Reference
=============

For detailed API documentation: :doc:`code/plugins`, :doc:`code/events`, :doc:`code/workflows`, :doc:`code/reportsenders`
