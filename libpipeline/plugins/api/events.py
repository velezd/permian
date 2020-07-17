from ...events.factory import EventFactory

def register(name, event_class=None):
    """
    Redirects to EventFactory.register

    TBD
    """
    return EventFactory.register(name, event_class)
