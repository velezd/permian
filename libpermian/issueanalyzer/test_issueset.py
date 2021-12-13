import unittest

from .issueset import IssueSet
from .base import BaseIssue

class TestIssueSet(unittest.TestCase):
    def setUp(self):
        self.i1 = unittest.mock.create_autospec(BaseIssue, instance=True)
        self.i2 = unittest.mock.create_autospec(BaseIssue, instance=True)
        self.i3 = unittest.mock.create_autospec(BaseIssue, instance=True)
        
    def testEmptyComplete(self):
        issueset = IssueSet()
        self.assertTrue(issueset.isComplete)
        self.assertFalse(issueset.needsReview)
        self.assertCountEqual(issueset.all, [])
        self.assertCountEqual(issueset.tracked, [])
        self.assertCountEqual(issueset.untracked, [])
        self.assertCountEqual(issueset.resolved, [])
        self.assertCountEqual(issueset.new, [])
        self.assertCountEqual(issueset.forReview, [])

    def testEmptyIncomplete(self):
        issueset = IssueSet(complete=False)
        self.assertFalse(issueset.isComplete)
        self.assertFalse(issueset.needsReview)
        self.assertCountEqual(issueset.all, [])
        self.assertCountEqual(issueset.tracked, [])
        self.assertCountEqual(issueset.untracked, [])
        self.assertCountEqual(issueset.resolved, [])
        self.assertCountEqual(issueset.new, [])
        self.assertCountEqual(issueset.forReview, [])

    def testNonemptyComplete(self):
        issueset = IssueSet([self.i1, self.i2])
        self.assertTrue(issueset.isComplete)
        self.assertCountEqual(issueset.all, [self.i1, self.i2])

    def testNonemptyIncomplete(self):
        issueset = IssueSet([self.i1, self.i2], False)
        self.assertFalse(issueset.isComplete)
        self.assertCountEqual(issueset.all, [self.i1, self.i2])

    def testTrackedUntracked(self):
        self.i1.tracked = True
        self.i2.tracked = False
        self.i3.tracked = True
        issueset = IssueSet([self.i1, self.i2, self.i3])
        self.assertCountEqual(issueset.tracked, [self.i1, self.i3])
        self.assertCountEqual(issueset.untracked, [self.i2])

    def testResolved(self):
        self.i1.resolved = True
        self.i2.resolved = True
        self.i3.resolved = False
        issueset = IssueSet([self.i1, self.i2, self.i3])
        self.assertCountEqual(issueset.resolved, [self.i1, self.i2])

    def testNew(self):
        self.i1.new = False
        self.i2.new = True
        self.i3.new = True
        issueset = IssueSet([self.i1, self.i2, self.i3])
        self.assertCountEqual(issueset.new, [self.i2, self.i3])

    def testReviewNone(self):
        self.i1.new = False
        self.i1.resolved = False
        self.i2.new = False
        self.i2.resolved = False
        self.i3.new = False
        self.i3.resolved = False
        issueset = IssueSet([self.i1, self.i2, self.i3])
        self.assertFalse(issueset.needsReview)
        self.assertCountEqual(issueset.forReview, [])

    def testReviewSome(self):
        self.i1.new = False
        self.i1.resolved = False
        self.i2.new = True
        self.i2.resolved = False
        self.i3.new = False
        self.i3.resolved = True
        issueset = IssueSet([self.i1, self.i2, self.i3])
        self.assertTrue(issueset.needsReview)
        self.assertCountEqual(issueset.forReview, [self.i2, self.i3])

    def testReviewAll(self):
        self.i1.new = True
        self.i1.resolved = True
        self.i2.new = True
        self.i2.resolved = False
        self.i3.new = False
        self.i3.resolved = True
        issueset = IssueSet([self.i1, self.i2, self.i3])
        self.assertTrue(issueset.needsReview)
        self.assertCountEqual(issueset.forReview, [self.i1, self.i2, self.i3])

    def testExtendAllComplete(self):
        issueset1 = IssueSet([self.i1, self.i2])
        issueset2 = IssueSet()
        issueset3 = IssueSet([self.i2, self.i3])
        for noop_extend in [], issueset2:
            issueset1.extend(noop_extend)
            self.assertTrue(issueset1.isComplete)
            self.assertCountEqual(issueset1.all, [self.i1, self.i2])
        issueset1.extend(issueset3)
        self.assertTrue(issueset1.isComplete)
        self.assertCountEqual(issueset1.all, [self.i1, self.i2, self.i3])

    def testExtendIncomplete(self):
        issueset1 = IssueSet([self.i1, self.i2], False)
        issueset2 = IssueSet()
        issueset3 = IssueSet([self.i2, self.i3])
        for noop_extend in [], issueset2:
            issueset1.extend(noop_extend)
            self.assertFalse(issueset1.isComplete)
            self.assertCountEqual(issueset1.all, [self.i1, self.i2])
        issueset1.extend(issueset3)
        self.assertFalse(issueset1.isComplete)
        self.assertCountEqual(issueset1.all, [self.i1, self.i2, self.i3])

    def testExtendWithIncomplete(self):
        issueset1 = IssueSet([self.i1, self.i2])
        issueset2 = IssueSet()
        issueset3 = IssueSet([self.i2, self.i3], False)
        for noop_extend in [], issueset2:
            issueset1.extend(noop_extend)
            self.assertTrue(issueset1.isComplete)
            self.assertCountEqual(issueset1.all, [self.i1, self.i2])
        issueset1.extend(issueset3)
        self.assertFalse(issueset1.isComplete)
        self.assertCountEqual(issueset1.all, [self.i1, self.i2, self.i3])

    def testExtendAllIncomplete(self):
        issueset1 = IssueSet([self.i1, self.i2], False)
        issueset2 = IssueSet(complete=False)
        issueset3 = IssueSet([self.i2, self.i3], False)
        for noop_extend in [], issueset2:
            issueset1.extend(noop_extend)
            self.assertFalse(issueset1.isComplete)
            self.assertCountEqual(issueset1.all, [self.i1, self.i2])
        issueset1.extend(issueset3)
        self.assertFalse(issueset1.isComplete)
        self.assertCountEqual(issueset1.all, [self.i1, self.i2, self.i3])
