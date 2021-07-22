import threading
import contextlib

from .issueset import IssueSet

class IssueAnalyzerProxy():
    """
    Issues are cached in issue_cache with key being unique issue identifier
    defined by implementation of BaseAnalyzer
    """
    issue_analyzers = set()

    @classmethod
    def register(cls, issue_analyzer):
        """
        Class decorator used for registering issue analyzers.
        Use this to assign name to the issue analyzer.

        :param issue_analyzer: 
        :type issue_analyzer: 
        """
        cls.issue_analyzers.add(issue_analyzer)
        return issue_analyzer

    def __init__(self, settings):
        self.settings = settings
        self._issue_cache = {}
        self._issue_cache_lock = threading.Lock()

    @property
    @contextlib.contextmanager
    def issue_cache(self):
        with self._issue_cache_lock:
            # Ensure that it's only possible to update the cache inside
            # the context and any update done out of it doesn't have any effect
            # on the cache.
            # Note the copy-update approach is definitely not the most
            # efficient and doesn't warn when the cache is used/updated out of
            # the context.
            # This protection may be improved or dropped later.
            cache_copy = self._issue_cache.copy()
            yield cache_copy
            self._issue_cache.update(cache_copy)

    def analyze(self, caseRunConfigurations):
        superIssueSet = IssueSet()

        for caseRunConfiguration in caseRunConfigurations:
            # consider crcs with final result as complete, if it's not complete
            # the analysis cannot be reliable
            issueSet = IssueSet(complete=caseRunConfiguration.result.final)
            for IssueAnalyzer in self.issue_analyzers:
                issueSet.extend(IssueAnalyzer.analyze(self, caseRunConfiguration))
            if not issueSet and caseRunConfiguration.result.result != "PASS":
                # No issue was found and the result is not PASS, so there
                # seems to be something missing, mark it as incomplete to
                # require review.
                superIssueSet.extend(IssueSet(complete=False))
            else:
                superIssueSet.extend(issueSet)
        return superIssueSet
