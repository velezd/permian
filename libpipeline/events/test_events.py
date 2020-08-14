import unittest
from libpipeline.events.factory import EventFactory
from libpipeline.events.base import Event

class TestEvent(Event):
    def __init__(self, event_type, payload, other_data):
        super().__init__(event_type, payload, other_data)

class TestEventFactory(unittest.TestCase):
    OLD_EVENT_TYPES = []

    @classmethod
    def setUpClass(cls):
        cls.OLD_EVENT_TYPES = EventFactory.EVENT_TYPES.copy()
        EventFactory.register('test')(TestEvent)

    @classmethod
    def tearDownClass(cls):
        EventFactory.EVENT_TYPES = cls.OLD_EVENT_TYPES

    def setUp(self):
        event_string = '''{"type" : "test",
                           "payload" : {"value" : "42"},
                           "test" : true}'''
        self.event = EventFactory.make(event_string)

    def test_registered(self):
        self.assertIs(TestEvent, EventFactory.EVENT_TYPES['test'])

    def test_payload(self):
        self.assertEqual(self.event.payload['value'], "42")

    def test_format_branch_spec(self):
        branch = self.event.format_branch_spec('Answer is {value}')
        self.assertEqual(branch, 'Answer is 42')

    def test_other_data(self):
        self.assertTrue(self.event.other_data['test'])
