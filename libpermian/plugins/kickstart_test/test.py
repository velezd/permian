import unittest
import os
import copy
import shutil

from libpermian.testruns import TestRuns
from libpermian.events.base import Event
from libpermian.settings import Settings

from tclib.library import Library

DUMMY_BOOT_ISO_URL = "file:///tmp/boot.iso"

OUTPUT_DUMP_FILE = "output.txt"
OUTPUT_DUMP_FILE_REGULAR = "kstest.daily-iso.stripped.log.txt"
OUTPUT_DUMP_FILE_MISSING = "kstest.daily-iso.stripped.log.missing.result.txt"
OUTPUT_DUMP_FILE_UNEXPECTED = "kstest.daily-iso.stripped.log.unexpected.result.txt"

EXPECTED_RESULTS = {
    OUTPUT_DUMP_FILE_REGULAR: {
        'authselect-not-set': ('complete', 'FAIL', True),
        'clearpart-1': ('complete', 'PASS', True),
        'container': ('complete', 'PASS', True),
        'keyboard-convert-vc': ('complete', 'PASS', True),
        'lang': ('complete', 'PASS', True),
        'packages-multilib': ('complete', 'FAIL', True),
        'selinux-permissive': ('complete', 'PASS', True),
        'services': ('complete', 'PASS', True),
    }
}


class TestFakePOCEvent(Event):
    def __init__(self, settings, event_type='kstest-poc'):
        super().__init__(
            settings,
            event_type,
            bootIso={
                'x86_64': DUMMY_BOOT_ISO_URL,
            },
        )


class TestKickstartTestWrorkflow(unittest.TestCase):
    """Basic test with dummy / noop launcher."""
    @classmethod
    def setUpClass(cls):
        cls.library = Library('./tests/test_library/kickstart-test/basic')
        cls.settings = Settings(
            cmdline_overrides={
                'kickstart_test': {
                    'runner_command': "echo containers/runner/launch",
                    'kstest_local_repo': "/tmp/mockrepo",
                },
            },
            environment={},
            settings_locations=[],
        )
        cls.event = TestFakePOCEvent(cls.settings)

    def setUp(self):
        self.testRuns = TestRuns(self.library, self.event, self.settings)
        self._ensure_file_exists(DUMMY_BOOT_ISO_URL[7:])

    def _ensure_file_exists(self, path):
        if not os.path.isfile(path):
            with open(path, 'w'):
                pass

    def testWorkflowRun(self):
        executed_workflows = set()
        for caseRunConfiguration in self.testRuns.caseRunConfigurations:
            with self.subTest(caseRunConfiguration=caseRunConfiguration):
                if id(caseRunConfiguration.workflow) not in executed_workflows:
                    caseRunConfiguration.workflow.run()
                    executed_workflows.add(id(caseRunConfiguration.workflow))
        self.assertEqual(len(executed_workflows), 1)


class TestKickstartTestWorkflowResultsParsing(unittest.TestCase):
    """Test parsing of results from output supplied by mocked launcher."""
    @classmethod
    def setUpClass(cls):
        library_rel_path = './tests/test_library/kickstart-test/results_parsing'
        cls.library_abs_path = os.path.join(os.getcwd(), library_rel_path)
        mock_launcher_path = os.path.join(cls.library_abs_path, "launch-mock.py")
        output_dump_path = os.path.join(cls.library_abs_path, OUTPUT_DUMP_FILE)

        cls.library = Library(library_rel_path)
        cls.settings = Settings(
            cmdline_overrides={
                'kickstart_test': {
                    'runner_command': "%s %s 1000 0" %
                    (mock_launcher_path, output_dump_path),
                    'kstest_local_repo': "/tmp/mockrepo",
                },
            },
            environment={},
            settings_locations=[],
        )
        cls.event = TestFakePOCEvent(cls.settings)

    def setUp(self):
        self.testRuns = TestRuns(self.library, self.event, self.settings)
        self._ensure_file_exists(DUMMY_BOOT_ISO_URL[7:])

    def _ensure_file_exists(self, path):
        if not os.path.isfile(path):
            with open(path, 'w'):
                pass

    def _run_with_expected_result(self, expected_result):
        executed_workflows = set()
        for caseRunConfiguration in self.testRuns.caseRunConfigurations:
            with self.subTest(caseRunConfiguration=caseRunConfiguration):
                if id(caseRunConfiguration.workflow) not in executed_workflows:
                    caseRunConfiguration.workflow.run()
                    executed_workflows.add(id(caseRunConfiguration.workflow))
        for caseRunConfiguration in self.testRuns.caseRunConfigurations:
            result = caseRunConfiguration.result
            self.assertEqual(
                (result.state, result.result, result.final),
                expected_result[caseRunConfiguration.testcase.name]
            )

    def _prepare_output_dump_file(self, dump_file):
        shutil.copyfile(
            os.path.join(self.library_abs_path, dump_file),
            os.path.join(self.library_abs_path, OUTPUT_DUMP_FILE),
        )

    def testResultsParsingRun(self):
        """Check individual test results parsed from output."""
        self._prepare_output_dump_file(OUTPUT_DUMP_FILE_REGULAR)
        self._run_with_expected_result(EXPECTED_RESULTS[OUTPUT_DUMP_FILE_REGULAR])

    def testResultsParsingRunWithUnexpectedResult(self):
        """Check individual test results parsed from output with unexpected result.

        The output contains test results of a test which is not in the test plan.
        """
        self._prepare_output_dump_file(OUTPUT_DUMP_FILE_UNEXPECTED)
        self._run_with_expected_result(EXPECTED_RESULTS[OUTPUT_DUMP_FILE_REGULAR])

    def testResultsParsingRunWithMissingResult(self):
        """Check individual test results parsed from output with missing result.

        The output is missing results of a test from the test plan.
        """
        self._prepare_output_dump_file(OUTPUT_DUMP_FILE_MISSING)
        expected_results = copy.copy(EXPECTED_RESULTS[OUTPUT_DUMP_FILE_REGULAR])
        expected_results['keyboard-convert-vc'] = ('running', None, False)
        self._run_with_expected_result(expected_results)
