import logging

from .factory import EventFactory
from .base import Event

LOGGER = logging.getLogger(__name__)

@EventFactory.register(None)
class UnknownEvent(Event):
    def __init__(self, event_type, **kwargs):
        super().__init__(event_type, **kwargs)
        LOGGER.error('Processing unknown event "%s", using just only provided structures: %s', event_type, kwargs)
