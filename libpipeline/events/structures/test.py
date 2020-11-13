import unittest

from ...exceptions import UnknownStructure
from ..factory import EventFactory
from ..base import Event
from .factory import EventStructuresFactory

class TestEvent(Event):
    pass

class FooStructure():
    pass

class BarStructure():
    def __init__(self, data):
        self.data = data

class BazStructure():
    def __init__(self, values):
        self.values = values

    @classmethod
    def from_bar(cls, structure):
        return cls(values=structure.data)

    @classmethod
    def from_foo(cls, structure):
        return cls([])
    
    def to_bar(self):
        return EventStructuresFactory.make("bar", {"data": self.values})

class TestStructuresFactory(unittest.TestCase):
    OLD_EVENT_STRUCTUR_TYPES = {}

    @classmethod
    def setUpClass(cls):
        cls.OLD_EVENT_STRUCTURE_TYPES = EventStructuresFactory.STRUCTURE_TYPES.copy()
        EventStructuresFactory.register('foo', FooStructure)
        EventStructuresFactory.register('bar', BarStructure)
        EventStructuresFactory.register('baz', BazStructure)

    @classmethod
    def tearDownClass(cls):
        EventStructuresFactory.STRUCTURE_TYPES = cls.OLD_EVENT_STRUCTURE_TYPES

    def test_empty_structure(self):
        structure = EventStructuresFactory.make("foo", {})
        self.assertIsInstance(structure, FooStructure)

    def test_nonempty_structure(self):
        structure = EventStructuresFactory.make("bar", {"data": [1,2,3]})
        self.assertIsInstance(structure, BarStructure)
        self.assertEqual(structure.data, [1,2,3])

    def test_unknown_structure(self):
        with self.assertRaises(UnknownStructure):
            EventStructuresFactory.make("unknown", {})

    def test_incorrect_field(self):
        with self.assertRaises(TypeError):
            EventStructuresFactory.make("foo", {"data": [1,2,3]})
        with self.assertRaises(TypeError):
            EventStructuresFactory.make("baz", {"data": [1,2,3]})

    def test_convert_baz_from_foo(self):
        foo = EventStructuresFactory.make("foo", {})
        baz = EventStructuresFactory.convert("baz", {"foo": foo})
        self.assertIsInstance(baz, BazStructure)
        self.assertEqual(baz.values, [])

    def test_convert_baz_from_bar(self):
        bar = EventStructuresFactory.make("bar", {"data": "hello"})
        baz = EventStructuresFactory.convert("baz", {"bar": bar})
        self.assertIsInstance(baz, BazStructure)
        self.assertEqual(baz.values, "hello")

    def test_convert_baz_to_bar(self):
        baz = EventStructuresFactory.make("baz", {"values": "hello"})
        bar = EventStructuresFactory.convert("bar", {"baz": baz})
        self.assertIsInstance(bar, BarStructure)
        self.assertEqual(bar.data, "hello")

    def test_convert_impossible(self):
        foo = EventStructuresFactory.make("foo", {})
        bar = EventStructuresFactory.convert("bar", {"foo": foo})
        self.assertIs(bar, NotImplemented)

    def test_convert_unknown(self):
        foo = EventStructuresFactory.make("foo", {})
        with self.assertRaises(UnknownStructure):
            EventStructuresFactory.convert("unknown", {"foo": foo})


class TestEventStructuresIntegration(unittest.TestCase):
    OLD_EVENT_TYPES = {}
    OLD_EVENT_STRUCTUR_TYPES = {}

    @classmethod
    def setUpClass(cls):
        cls.OLD_EVENT_TYPES = EventFactory.EVENT_TYPES.copy()
        cls.OLD_EVENT_STRUCTURE_TYPES = EventStructuresFactory.STRUCTURE_TYPES.copy()
        EventFactory.register('test')(TestEvent)
        EventStructuresFactory.register('foo', FooStructure)
        EventStructuresFactory.register('bar', BarStructure)
        EventStructuresFactory.register('baz', BazStructure)

    @classmethod
    def tearDownClass(cls):
        EventFactory.EVENT_TYPES = cls.OLD_EVENT_TYPES
        EventStructuresFactory.STRUCTURE_TYPES = cls.OLD_EVENT_STRUCTURE_TYPES

    def test_unknown_structure(self):
        with self.assertRaises(UnknownStructure):
            EventFactory.make('{"type": "test", "unknown": {}}')

    def test_incorrect_field(self):
        with self.assertRaises(TypeError):
            EventFactory.make('{"type": "test", "foo": {"data": [1,2,3]}}')
        with self.assertRaises(TypeError):
            EventFactory.make('{"type": "test", "baz": {"data": [1,2,3]}}')

    def test_baz_from_foo(self):
        event = EventFactory.make('{"type": "test", "foo": {}}')
        self.assertCountEqual(event.structures.keys(), ["foo"])
        self.assertIsInstance(event.structures['foo'], FooStructure)
        self.assertIsInstance(event.baz, BazStructure)
        self.assertCountEqual(event.structures.keys(), ["foo", "baz"])
        self.assertEqual(event.baz.values, [])

    def test_baz_from_bar(self):
        event = EventFactory.make('{"type": "test", "bar": {"data": "hello"}}')
        self.assertCountEqual(event.structures.keys(), ["bar"])
        self.assertIsInstance(event.structures['bar'], BarStructure)
        self.assertIsInstance(event.baz, BazStructure)
        self.assertCountEqual(event.structures.keys(), ["bar", "baz"])
        self.assertEqual(event.baz.values, "hello")

    def test_baz_to_bar(self):
        event = EventFactory.make('{"type": "test", "baz": {"values": "hello"}}')
        self.assertCountEqual(event.structures.keys(), ["baz"])
        self.assertIsInstance(event.structures['baz'], BazStructure)
        self.assertIsInstance(event.bar, BarStructure)
        self.assertCountEqual(event.structures.keys(), ["bar", "baz"])
        self.assertEqual(event.bar.data, "hello")

    def test_convert_impossible(self):
        event = EventFactory.make('{"type": "test", "foo": {}}')
        self.assertIsNone(event.bar)

    def test_not_structure(self):
        event = EventFactory.make('{"type": "test", "foo": {}}')
        with self.assertRaises(AttributeError):
            event.unknown
