import unittest
import os

from libpermian.testruns import TestRuns
from libpermian.events.base import Event
from libpermian.settings import Settings

from tclib.library import Library

DUMMY_BOOT_ISO_URL = "file:///tmp/boot.iso"


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
    @classmethod
    def setUpClass(cls):
        cls.library = Library('./tests/test_library/')
        cls.settings = Settings(
            cmdline_overrides={
                'kickstart_test': {
                    'runner_command': "echo containers/runner/launch"
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
