class UnexpectedState(Exception):
    """
    Signal that the code reached point which shouldn't have been reached.
    """
    pass

class NotReady(Exception):
    """
    Signal that some action happened out of expected order.
    """
    pass

class StateChangeError(Exception):
    """
    Raised in cases of invalid state changes.
    """
    pass

class UnknownCommandError(Exception):
    """
    Raised when the pipeline is called with unknown command.
    """
    pass

class LibraryNotFound(Exception):
    """
    Raised when pipeline couldn't obtain library.
    """
    def __init__(self, repoURL, attempted_branches):
        self.repoURL = repoURL
        self.attempted_branches = attempted_branches
        super().__init__(self, f"Couldn't clone repository from '{repoURL}'. Attemted branches: '{attempted_branches}'")

class UnknownTestConfigurationMergeMethod(Exception):
    """
    Raised when merge method used durring merge of test configurations in testplan and testcase doesn't exist
    """
    def __init__(self, method):
        super().__init__('Unknown testcase configurations merge method: %s' % method)

class ReadOnlyChangeError(Exception):
    """
    Raised when some read-only object is attempted to be updated/changed.
    """
    pass

class UnknownStructure(Exception):
    """
    Raised when unknown structure is encountered
    """
    def __init__(self, name):
        self.name = name
        super().__init__(f"Unknown structure: '{name}'")
