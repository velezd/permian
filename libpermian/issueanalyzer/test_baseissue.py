import unittest
import logging
import contextlib

from libpermian.settings import Settings

from .proxy import IssueAnalyzerProxy
from .base import BaseAnalyzer, BaseIssue
from .issueset import IssueSet

LOGGER = logging.getLogger('test')

class NewIssue(BaseIssue):
    def submit(self):
        LOGGER.info('submit was called')
        return super().submit()

    def make(self):
        LOGGER.info('make was called')
        return 'http://issuetracker.example.com/new_issue'

    def update(self):
        LOGGER.info('update was called')

    def _lookup(self):
        LOGGER.info('lookup was called')
        return None

    @property
    def resolved(self):
        return False

    @property
    def report_url(self):
        return 'http://issuetracker.example.com/new/foo'

class TrackedUnresolvedIssue(NewIssue):
    def _lookup(self):
        LOGGER.info('lookup was called')
        return 'http://issuetracker.example.com/123'

    @property
    def resolved(self):
        return False

    @property
    def report_url(self):
        return 'http://issuetracker.example.com/new/bar'

class TrackedResolvedIssue(TrackedUnresolvedIssue):
    @property
    def resolved(self):
        return True

class TestNewIssue(unittest.TestCase):
    def setUp(self):
        self.settings = Settings({}, {}, [])
        self.issue = NewIssue(self.settings)

    def test_properties(self):
        self.assertTrue(self.issue.new)
        self.assertFalse(self.issue.tracked)
        self.assertEqual(self.issue.uri, None)

    def test_sync(self):
        # test lookup was called
        with self.assertLogs('test', level='INFO') as cm:
            self.issue.sync()
        self.assertEqual(cm.output, ['INFO:test:lookup was called'])
        self.test_properties()

    def test_str(self):
        self.assertEqual(str(self.issue), self.issue.report_url)

class TestTrackedUnresolvedIssue(TestNewIssue):
    def setUp(self):
        self.settings = Settings({}, {}, [])
        self.issue = TrackedUnresolvedIssue(self.settings)

    def test_properties(self):
        self.assertFalse(self.issue.new)
        self.assertTrue(self.issue.tracked)
        self.assertEqual(self.issue.uri, 'http://issuetracker.example.com/123')

    def test_str(self):
        self.assertEqual(str(self.issue), self.issue.uri)

# TrackedResolvedIssue should behave the same way as TrackedUnresolvedIssue
# so just inherit the whole test case to run the very same test
class TestTrackedResolvedIssue(TestTrackedUnresolvedIssue):
    def setUp(self):
        self.settings = Settings({}, {}, [])
        self.issue = TrackedResolvedIssue(self.settings)

class TestSubmitDisabled(unittest.TestCase):
    settings = Settings(
        {
            'issueAnalyzer' : {
                'create_issues': False,
                'update_issues': False,
                'create_issues_instead_of_update': False,
            }
        },
        {},
        []
    )

    def setUp(self):
        self.new = NewIssue(self.settings)
        self.unresolved = TrackedUnresolvedIssue(self.settings)
        self.resolved = TrackedResolvedIssue(self.settings)
        # sync the issues so that lookup is not called => logged during submit
        self.new.sync()
        self.unresolved.sync()
        self.resolved.sync()

    @contextlib.contextmanager
    def assertUnchanged(self, issue):
        old_uri = issue.uri
        old_new = issue.new
        old_tracked = issue.tracked
        yield issue
        self.assertEqual(issue.uri, old_uri)
        self.assertEqual(issue.new, old_new)
        self.assertEqual(issue.tracked, old_tracked)

    def assertSubmitNoop(self, issue):
        with self.assertUnchanged(issue):
            with self.assertLogs('test', level='INFO') as cm:
                issue.submit()
                issue.submit()
        self.assertEqual(cm.output, [
            "INFO:test:submit was called",
            "INFO:test:submit was called",
        ])

    def assertSubmitCreate(self, issue):
        with self.assertLogs('test', level='INFO') as cm:
            result1 = issue.submit()
            result2 = issue.submit()
        self.assertEqual(cm.output, [
            "INFO:test:submit was called",
            "INFO:test:make was called",
            "INFO:test:submit was called",
        ])
        self.assertEqual(result1, result2)
        return result1

    def assertSubmitUpdate(self, issue):
        with self.assertUnchanged(issue):
            with self.assertLogs('test', level='INFO') as cm:
                result1 = issue.submit()
                result2 = issue.submit()
        self.assertEqual(cm.output, [
            "INFO:test:submit was called",
            "INFO:test:update was called",
            "INFO:test:submit was called",
        ])
        self.assertEqual(result1, result2)
        return result1

    def testNew(self):
        self.assertSubmitNoop(self.new)

    def testUnresolved(self):
        self.assertSubmitNoop(self.unresolved)

    def testResolved(self):
        self.assertSubmitNoop(self.resolved)

class TestSubmitCreateUpdate(TestSubmitDisabled):
    settings = Settings(
        {
            'issueAnalyzer' : {
                'create_issues': True,
                'update_issues': True,
                'create_issues_instead_of_update': False,
            }
        },
        {},
        []
    )

    def testNew(self):
        result = self.assertSubmitCreate(self.new)
        self.assertTrue(self.new.new)
        self.assertTrue(self.new.tracked)
        self.assertEqual(result, 'http://issuetracker.example.com/new_issue')
        self.assertEqual(result, self.new.uri)
        # repeated submit doesn't do anything
        with self.assertUnchanged(self.new):
            with self.assertLogs('test', level='INFO') as cm:
                result = self.new.submit()
        self.assertEqual(cm.output, [
            "INFO:test:submit was called",
        ])

    def testUnresolved(self):
        self.assertSubmitUpdate(self.unresolved)
        
    def testResolved(self):
        self.assertSubmitUpdate(self.resolved)

class TestSubmitCreateOnlyNew(TestSubmitCreateUpdate):
    settings = Settings(
        {
            'issueAnalyzer' : {
                'create_issues': True,
                'update_issues': False,
                'create_issues_instead_of_update': False,
            }
        },
        {},
        []
    )

    def testUnresolved(self):
        self.assertSubmitNoop(self.unresolved)

    def testResolved(self):
        self.assertSubmitNoop(self.resolved)

class TestSubmitUpdateOnlyTracked(TestSubmitCreateUpdate):
    settings = Settings(
        {
            'issueAnalyzer' : {
                'create_issues': False,
                'update_issues': True,
                'create_issues_instead_of_update': False,
        }
        },
        {},
        []
    )

    def testNew(self):
        self.assertSubmitNoop(self.new)

class TestSubmitCreateAlwaysWithUpdateOff(TestSubmitCreateUpdate):
    settings = Settings(
        {
            'issueAnalyzer' : {
                'create_issues': True,
                'update_issues': False, # This should have no effect
                'create_issues_instead_of_update': True,
            }
        },
        {},
        []
    )

    def testUnresolved(self):
        old_uri = self.unresolved.uri
        result = self.assertSubmitCreate(self.unresolved)
        self.assertEqual(result, 'http://issuetracker.example.com/new_issue')
        self.assertEqual(self.unresolved.uri, result)
        self.assertNotEqual(result, old_uri)

    def testResolved(self):
        old_uri = self.resolved.uri
        result = self.assertSubmitCreate(self.resolved)
        self.assertEqual(result, 'http://issuetracker.example.com/new_issue')
        self.assertEqual(self.resolved.uri, result)
        self.assertNotEqual(result, old_uri)

# The update_issue should have no effect when create_issues_instead_of_update
# is set to True.
class TestSubmitCreateAlwaysWithUpdateOn(TestSubmitCreateAlwaysWithUpdateOff):
    settings = Settings(
        {
            'issueAnalyzer' : {
                'create_issues': True,
                'update_issues': True, # This should have no effect
                'create_issues_instead_of_update': True,
            }
        },
        {},
        []
    )
