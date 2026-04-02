=======
Testing
=======

Overview
========

Permian uses a comprehensive testing strategy with three types of tests:

1. **Lint tests** - Code quality checks using pylint
2. **Unit tests** - Fast, isolated tests of individual components
3. **Integration tests** - End-to-end tests of complete workflows

All tests can be run using the Makefile targets inside the container::

    ./in_container make test              # Run all tests
    ./in_container make test.lint         # Run only lint tests
    ./in_container make test.unit         # Run only unit tests
    ./in_container make test.integration  # Run only integration tests

Test Organization
=================

Directory Structure
-------------------

Tests are organized as follows::

    permian/
    ├── libpermian/                    # Source code
    │   ├── events/
    │   │   └── test_events.py         # Unit tests alongside source
    │   ├── plugins/
    │   │   ├── compose/
    │   │   │   └── test_compose.py    # Plugin unit tests
    │   │   └── test_plugins.py        # Plugin system tests
    │   └── ...
    ├── tests/                         # Test-specific files
    │   ├── integration/               # Integration test suites
    │   │   ├── test_example/          # One directory per test suite
    │   │   │   └── test_0.sh          # Shell-based integration test
    │   │   └── test_testing_plugin/
    │   │       ├── test_1.sh
    │   │       └── test_1_result/     # Expected results
    │   ├── plugins/                   # Test plugin fixtures
    │   │   ├── test1_enabled/
    │   │   └── test2_disabled/
    │   ├── test_library/              # Test library for integration tests
    │   └── test_settings.ini          # Test configuration
    ├── run_unit_tests.py              # Unit test runner
    ├── run_integration_tests.sh       # Integration test runner
    └── run_pylint.sh                  # Linter

Unit Tests
==========

Unit tests use Python's built-in ``unittest`` framework and test individual components in isolation.

Writing Unit Tests
------------------

Unit test files are named ``test_*.py`` and placed alongside the source code they test.

**Basic Structure:**

.. code-block:: python

    import unittest
    from unittest.mock import patch, MagicMock

    class TestMyComponent(unittest.TestCase):
        def setUp(self):
            """Called before each test method."""
            pass

        def tearDown(self):
            """Called after each test method."""
            pass

        @classmethod
        def setUpClass(cls):
            """Called once before all tests in the class."""
            pass

        @classmethod
        def tearDownClass(cls):
            """Called once after all tests in the class."""
            pass

        def test_basic_functionality(self):
            """Test names must start with 'test_'."""
            self.assertEqual(2 + 2, 4)

Mocking
-------

Use ``unittest.mock`` for isolating components:

**Common Mock Patterns:**

.. code-block:: python

    from unittest.mock import patch, MagicMock, call

    # Mock environment variables
    @patch('os.environ', new={'VAR': 'value'})
    def test_with_env(self):
        pass

    # Mock function calls
    class ResultMock200():
        status_code = 200
        text = 'test'

        @classmethod
        def json(cls):
            return {'head': {'sha': 'abc123'}}

    @patch('requests.get')
    def test_reporting(self, requests_get):
        requests_get.return_value = ResultMock200()

Running Unit Tests
------------------

Unit tests are discovered and run using script::

    ./run_unit_tests.py

Or inside the container::

    ./in_container make test.unit

The test runner:

1. Discovers all ``test*.py`` in project root and all loaded plugin directories
2. Runs all discovered tests
3. Exits with code 2 if any test fails, debug output written to ``test_debug.log``

Integration Tests
=================

Integration tests verify complete workflows by running the pipeline with real or simulated inputs and comparing output to expected results.

Writing Integration Tests
-------------------------

Integration tests are bash scripts that define three functions: ``setup``, ``test``, and ``cleanup``.

**Basic Structure:**

.. code-block:: bash

    setup() {
        echo "Test description"
        # Prepare test environment
        TEST_REPORT_DIR=$(mktemp -d)
    }

    test() {
        # Run the pipeline or specific commands
        ./pipeline example -o library.directPath=./tests/test_library

        # Optionally compare results
        diff -Naur expected_result $TEST_REPORT_DIR
    }

    cleanup() {
        # Clean up resources
        rm -rf $TEST_REPORT_DIR
    }

Running Integration Tests
--------------------------

Integration tests are run using::

    ./run_integration_tests.sh

Or inside the container::

    ./in_container make test.integration

The runner:

1. Discovers all ``test_*.sh`` files in ``tests/integration/*/``
2. For each test:

   - Runs ``setup()`` (exits if setup fails)
   - Runs ``test()`` (marks as PASSED or FAILED)
   - Runs ``cleanup()`` (reports if cleanup fails)

3. Exits with:

   - ``0`` - All tests passed
   - ``1`` - One or more tests failed
   - ``2`` - Setup error
   - ``3`` - Cleanup error

Lint Tests
==========

Pylint is used to check code quality and catch common errors.

Running Lint Tests
------------------

Linting is run using script::

    ./run_pylint.sh

Or inside the container::

    ./in_container make test.lint

The linter checks:

- Core libpermian code
- All loaded plugins (discovered via ``python3 -m libpermian.plugins list --paths``)
- Only errors are reported (``-E`` flag)

Pylint configuration is in ``.pylintrc``

Continuous Integration
======================

Tests are designed to run in CI environments. Github Actions is used to run all tests and build documentation on every pull request.
No change should be merged without all tests passing.
