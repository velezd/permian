from ...events.factory import EventFactory
from ...events.structures.factory import EventStructuresFactory

def register(name, event_class=None):
    """
    Redirects to EventFactory.register

    TBD
    """
    return EventFactory.register(name, event_class)

def register_structure(name, event_class=None):
    """
    Redirects to EventStructuresFactory.register

    TBD
    """
    return EventStructuresFactory.register(name, event_class)
