import abc
import threading

from .issueset import IssueSet

# Note: This could be just a regular callable
class BaseAnalyzer(metaclass=abc.ABCMeta):
    @staticmethod
    @abc.abstractmethod
    def analyze(analyzerProxy, caseRunConfiguration):
        pass

class BaseIssue(metaclass=abc.ABCMeta):
    settings_sections = ['issueAnalyzer']

    def __init__(self, settings):
        self.settings = settings
        self._synced = False
        self._new = None
        self._uri = None
        self._submitted = False
        self._lock = threading.RLock()

    def submit(self):
        with self._lock:
            if self._submitted:
                return self._uri
            self.sync()
            if not self.tracked or self.create_issues_instead_of_update:
                if self.create_issues:
                    self._uri = self.make()
            elif self.tracked and self.update_issues:
                self.update()
            self._submitted = True
        return self._uri

    @abc.abstractmethod
    def make(self):
        pass

    @abc.abstractmethod
    def update(self):
        pass

    @abc.abstractmethod
    def _lookup(self):
        """
        Lookup the issue in the issue database and return the URI of the issue.

        :return: URI of this issue in the issue database
        :rtype: list
        """
        pass

    @property
    def new(self):
        self.sync()
        return self._new

    @property
    def tracked(self):
        self.sync()
        return self.uri is not None

    @property
    def uri(self):
        self.sync()
        return self._uri

    @property
    @abc.abstractmethod
    def resolved(self):
        pass

    @property
    @abc.abstractmethod
    def report_url(self):
        pass

    def sync(self, force=False):
        """
        Sync the status of the issue by looking it up in the issue database.

        :param force: Perform the sync even if the sync was already done for this issue. Note that this won't overwrite the "new" status to prevent incorrect interpretation if the make method was called between the syncs.
        :type force: boolean
        :rtype: None
        """
        with self._lock:
            if not force and self._synced:
                return
            self._uri = self._lookup()
            # don't update "new" state in case of subsequent force sync
            if self._new is None:
                self._new = self._uri is None
            self._synced = True

    def __str__(self):
        self.sync()
        return self.uri or self.report_url

    def __repr__(self):
        return f"<{type(self).__name__}({str(self)}, resolved={self.resolved})>"

    @property
    def create_issues_instead_of_update(self):
        return self.settings.getboolean(
            self.settings_sections,
            'create_issues_instead_of_update',
        )

    @property
    def create_issues(self):
        return self.settings.getboolean(
            self.settings_sections,
            'create_issues',
        )

    @property
    def update_issues(self):
        return self.settings.getboolean(
            self.settings_sections,
            'update_issues',
        )
