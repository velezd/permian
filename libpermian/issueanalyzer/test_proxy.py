import unittest

from .proxy import IssueAnalyzerProxy
from .base import BaseAnalyzer, BaseIssue
from .issueset import IssueSet
from libpermian.caserunconfiguration import CaseRunConfiguration
from libpermian.pipeline import Pipeline

# share common setUp and tearDown between test cases, but not tests
class TestIssueAnalyzerProxyCommon(unittest.TestCase):
    def setUp(self):
        self.originalIssueAnalyzers = IssueAnalyzerProxy.issue_analyzers
        IssueAnalyzerProxy.issue_analyzers = set()
        self.AnalyzerClass1 = unittest.mock.create_autospec(BaseAnalyzer)
        self.AnalyzerClass2 = unittest.mock.create_autospec(BaseAnalyzer)
        self.AnalyzerClass1.analyze.return_value = []
        self.AnalyzerClass2.analyze.return_value = []
        # unittest.mock.create_autospec(CaseRunConfiguration, instance=True)
        # cannot be used as the IssueAnalyzerProxy accesses the result
        # attribute so instance of CaseRunConfiguration is needed as it has
        # attributes set by __init__
        fake_crc = CaseRunConfiguration(None, None, [])
        self.crc1 = unittest.mock.create_autospec(fake_crc, spec_set=True)
        self.crc2 = unittest.mock.create_autospec(fake_crc, spec_set=True)
        self.crc3 = unittest.mock.create_autospec(fake_crc, spec_set=True)
        self.caseRunConfigurations = [self.crc1, self.crc2, self.crc3]
        # make all crcs final with PASS result. Individual test cases can
        # change the result and/or final
        for crc in self.caseRunConfigurations:
            crc.result.final = True
            crc.result.result = "PASS"
        self.analyzerProxy = IssueAnalyzerProxy(
            unittest.mock.create_autospec(Pipeline, instance=True)
        )

    def tearDown(self):
        IssueAnalyzerProxy.issue_analyzers = self.originalIssueAnalyzers

class TestIssueAnalyzerProxyRegister(TestIssueAnalyzerProxyCommon):
    def test_register(self):
        self.assertEqual(
            IssueAnalyzerProxy.register(self.AnalyzerClass1),
            self.AnalyzerClass1,
        )
        self.assertCountEqual(
            IssueAnalyzerProxy.issue_analyzers,
            [self.AnalyzerClass1],
        )
        self.assertEqual(
            IssueAnalyzerProxy.register(self.AnalyzerClass2),
            self.AnalyzerClass2,
        )
        self.assertCountEqual(
            IssueAnalyzerProxy.issue_analyzers,
            [self.AnalyzerClass1, self.AnalyzerClass2],
        )
        self.AnalyzerClass1.assert_not_called()
        self.AnalyzerClass2.assert_not_called()

    def test_analyze(self):
        IssueAnalyzerProxy.register(self.AnalyzerClass1)
        IssueAnalyzerProxy.register(self.AnalyzerClass2)
        result = self.analyzerProxy.analyze(self.caseRunConfigurations)
        expected_calls = [
            unittest.mock.call(self.analyzerProxy, caseRunConfiguration)
            for caseRunConfiguration
            in self.caseRunConfigurations
        ]
        self.AnalyzerClass1.analyze.assert_has_calls(expected_calls)
        self.AnalyzerClass2.analyze.assert_has_calls(expected_calls)
        self.assertIsInstance(result, IssueSet)
        self.assertCountEqual(result.all, [])
        self.assertTrue(result.isComplete)

class TestIssueAnalyzerProxyAnalyze(TestIssueAnalyzerProxyCommon):
    def setUp(self):
        super().setUp()
        IssueAnalyzerProxy.register(self.AnalyzerClass1)
        IssueAnalyzerProxy.register(self.AnalyzerClass2)

    def tearDown(self):
        IssueAnalyzerProxy.issue_analyzers = self.originalIssueAnalyzers

    def test_analyze_passed_crcs_without_issues(self):
        result = self.analyzerProxy.analyze(self.caseRunConfigurations)
        expected_calls = [
            unittest.mock.call(self.analyzerProxy, caseRunConfiguration)
            for caseRunConfiguration
            in self.caseRunConfigurations
        ]
        self.assertCountEqual(result.all, [])
        self.assertTrue(result.isComplete)

    def test_analyze_passed_crcs_with_issues(self):
        issue1 = unittest.mock.create_autospec(BaseIssue, instance=True)
        issue2 = unittest.mock.create_autospec(BaseIssue, instance=True)
        issue3 = unittest.mock.create_autospec(BaseIssue, instance=True)
        self.AnalyzerClass1.analyze.return_value = [issue1, issue2]
        self.AnalyzerClass2.analyze.return_value = [issue3]
        result = self.analyzerProxy.analyze(self.caseRunConfigurations)
        self.assertCountEqual(result.all, [issue1, issue2, issue3])
        self.assertTrue(result.isComplete)

    def test_analyze_failed_crc_without_issue(self):
        # crc2 is FAIL but no analyzer provides issue for it
        self.crc1.result.result = "FAIL"
        self.crc2.result.result = "FAIL"
        issue1 = unittest.mock.create_autospec(BaseIssue, instance=True)
        def fake_analyze(proxy, crc):
            if crc == self.caseRunConfigurations[0]:
                return [issue1]
            return []
        self.AnalyzerClass1.analyze = fake_analyze
        result = self.analyzerProxy.analyze(self.caseRunConfigurations)
        self.assertCountEqual(result.all, [issue1])
        self.assertFalse(result.isComplete)

    def test_analyze_failed_crcs_with_issues(self):
        # crc1 and crc2 are FAIL with issues provided by at least one analyzer
        self.crc1.result.result = "FAIL"
        self.crc2.result.result = "FAIL"
        issue1 = unittest.mock.create_autospec(BaseIssue, instance=True)
        issue2 = unittest.mock.create_autospec(BaseIssue, instance=True)
        def fake_analyze1(proxy, crc):
            if crc == self.caseRunConfigurations[0]:
                return [issue1]
            return []
        self.AnalyzerClass1.analyze = fake_analyze1
        def fake_analyze2(proxy, crc):
            if crc == self.caseRunConfigurations[1]:
                return [issue2]
            return []
        self.AnalyzerClass2.analyze = fake_analyze2
        result = self.analyzerProxy.analyze(self.caseRunConfigurations)
        self.assertCountEqual(result.all, [issue1, issue2])
        self.assertTrue(result.isComplete)

    def test_analyze_passed_crcs_incomplete(self):
        self.crc1.result.final = False
        result = self.analyzerProxy.analyze(self.caseRunConfigurations)
        self.assertCountEqual(result.all, [])
        self.assertFalse(result.isComplete)

    def test_analyze_mixed_crcs_incomplete_with_issues(self):
        self.crc2.result.result = "FAIL"
        self.crc3.result.result = "FAIL"
        self.crc3.result.final = False
        issue = unittest.mock.create_autospec(BaseIssue, instance=True)
        self.AnalyzerClass1.analyze.return_value = [issue]
        result = self.analyzerProxy.analyze(self.caseRunConfigurations)
        self.assertCountEqual(result.all, [issue])
        self.assertFalse(result.isComplete)

class TestIssueAnalyzerProxyCache(TestIssueAnalyzerProxyCommon):
    def test_cache(self):
        self.assertFalse(self.analyzerProxy._issue_cache_lock.locked())
        with self.analyzerProxy.issue_cache as issue_cache:
            self.assertTrue(self.analyzerProxy._issue_cache_lock.locked())
            self.assertEqual(issue_cache, dict())
            issue_cache['foo'] = 'bar'
        self.assertFalse(self.analyzerProxy._issue_cache_lock.locked())
        # test cache out of context protection
        self.assertIsNot(issue_cache, self.analyzerProxy._issue_cache)
        issue_cache['dirt'] = 'mud'
        # check the cache contains changes done only inside cache context
        with self.analyzerProxy.issue_cache as issue_cache:
            self.assertTrue(self.analyzerProxy._issue_cache_lock.locked())
            self.assertEqual(issue_cache, {"foo": "bar"})
