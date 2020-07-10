import logging

from .factory import EventFactory
from .base import Event

LOGGER = logging.getLogger(__name__)

@EventFactory.register(None)
class UnknownEvent(Event):
    def __init__(self, event_type, payload, other_data):
        super().__init__(event_type, payload, other_data)
        LOGGER.error('Processing unknown event "%s", using just only provided payload: %s', event_type, payload)
