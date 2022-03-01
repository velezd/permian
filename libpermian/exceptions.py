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

class LocalLogExistsError(Exception):
    """
    Raised when trying to change path to log which already exists and has different path.
    """
    def __init__(self, crcid, name, old_path, new_path):
        msg = f"Cannot change path for log '{name}' of crcId: {crcid}. Old path: '{old_path}', new path: '{new_path}'"
        self.crcid = crcid
        self.name = name
        self.old_path = old_path
        self.new_path = new_path
        super().__init__(msg)

class RemoteLogError(Exception):
    """
    Raised when trying to access remote log in incompatible way.
    """
    def __init__(self, crcid, name, log_path):
        msg = f"Cannot open remote logfile: '{log_path}' for log '{name}' of crcId: {crcid}"
        self.crcid = crcid
        self.name = name
        self.log_path = log_path
        super().__init__(msg)

class ResourceNotAvailable(Exception):
    """
    Raised when desired resource is not available. The purpose is to signal
    that some resource should be available (according to the settings), but
    it's not available.
    """
    def __init__(self, msg):
        super().__init__(msg)

class StructureConversionError(Exception):
    """ Raised when confersion of event structure fails """
    def __init__(self, from_structure, to_structure, reason):
        super().__init__(f"Conversion from '{from_structure.__name__}' to '{to_structure.__name__}' has failed, {reason}")

class UnsupportedConfiguration(Exception):
    """
    Raised for test configuration value not supported by workflow.
    """
    def __init__(self, configuration, value):
        msg = f"Configuration '{configuration}: {value}' is not supported"
        self.configuration = configuration
        self.value = value
        super().__init__(msg)
