import json

class EventFactory():
    EVENT_TYPES = {}

    @classmethod
    def register(cls, event_type, event_class=None):
        def decorator(event_class):
            cls.EVENT_TYPES[event_type] = event_class
            return event_class
        if event_class is not None:
            return decorator(event_class)
        return decorator

    @classmethod
    def make(cls, data):
        data = json.loads(data)
        event_type = data.pop('type')
        event_payload = data.pop('payload')
        event_class = cls.EVENT_TYPES.get(event_type, cls.EVENT_TYPES[None])
        return event_class(event_type, event_payload, data)
