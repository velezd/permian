class Event():
    """
    Base class of event which takes the event payload and stores it in payload
    property. The type is stored in the type property.
    """
    def __init__(self, event_type, payload, other_data):
        self.type = event_type
        self.payload = self.process_payload(payload)
        self.other_data = other_data

    def process_payload(self, payload):
        return payload

    def format_branch_spec(self, fmt):
        return fmt.format(**self.payload)
