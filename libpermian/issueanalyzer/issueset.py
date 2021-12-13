class IssueSet(set):
    def __init__(self, issues=None, complete=True):
        self._complete = complete
        if issues is not None:
            self.extend(issues)

    def extend(self, issues):
        self.update(issues)
        try:
            self._complete &= issues.isComplete
        except AttributeError:
            pass

    @property
    def isComplete(self):
        return self._complete

    @property
    def needsReview(self):
        """
        Return True if result/issue review is needed for any of the issue in
        this issueSet. A review is needed if the found issue is considered to
        be fixed (but it was detected) or if there's some new (previously
        untracked) issue.
        """
        return any(i.new or i.resolved for i in self)

    @property
    def forReview(self):
        """
        Return issues that are subject for review. Issues that are either new
        or resolved (but it was detected) are subject for review and should
        result either in update of the issue and/or change of the test.
        """
        return (i for i in self if i.new or i.resolved)

    @property
    def all(self):
        return (i for i in self)

    @property
    def tracked(self):
        return (i for i in self if i.tracked)

    @property
    def untracked(self):
        return (i for i in self if not i.tracked)

    @property
    def resolved(self):
        return (i for i in self if i.resolved)

    @property
    def new(self):
        return (i for i in self if i.new)
