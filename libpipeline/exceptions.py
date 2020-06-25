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
