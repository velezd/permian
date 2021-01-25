import unittest
import re
from unittest.mock import patch, create_autospec
import productmd

from libpipeline.cli.factory import CliFactory
from libpipeline.events.factory import EventFactory

class MockComposeResponse():
    def __init__(self, url):
        self.url = url
    def geturl(self):
        return self.url.replace('example.com/compose', 'example.com/here')

def MockProductmdCompose(location):
    instance = create_autospec(productmd.compose.Compose)(location)
    if '.n.' in location:
        instance.info.compose.type = "nightly"
        instance.info.compose.label = None
    else:
        instance.info.compose.type = "production"
        instance.info.compose.label = "Hello-3.14"
    return instance

class MockUrlopen():
    def __init__(self, url):
        self.url = url
    def __enter__(self):
        return MockComposeResponse(self.url)
    def __exit__(self, type, value, traceback):
        pass

@patch('productmd.compose.Compose', new=MockProductmdCompose)
@patch('urllib.request.urlopen', new=MockUrlopen)
class TestEventCompose(unittest.TestCase):
    def test_rhel_idonly(self):
        event = EventFactory.make(CliFactory.parse('compose', ['RHEL-8.3.0-20200701.2'])[1])
        self.assertEqual(event.compose.id, 'RHEL-8.3.0-20200701.2')
        self.assertEqual(event.compose.version, '8.3.0')
        self.assertEqual(event.compose.major, '8')
        self.assertEqual(event.compose.minor, '3')
        self.assertEqual(event.compose.qr, '0')
        self.assertEqual(event.compose.spin, '2')
        self.assertEqual(event.compose.date, '20200701')
        self.assertEqual(event.compose.product, 'RHEL')
        self.assertIsNone(event.compose.parent_product)
        self.assertIsNone(event.compose.parent_version)
        self.assertFalse(event.compose.nightly)
        self.assertFalse(event.compose.layered)
        self.assertEqual(event.compose.location, 'http://example.com/here/RHEL-8.3.0-20200701.2')

    def test_supp_idonly(self):
        event = EventFactory.make(CliFactory.parse('compose', ['Supp-9.2.1-RHEL-8-20200811.n.5'])[1])
        self.assertEqual(event.compose.id, 'Supp-9.2.1-RHEL-8-20200811.n.5')
        self.assertEqual(event.compose.version, '9.2.1')
        self.assertEqual(event.compose.major, '9')
        self.assertEqual(event.compose.minor, '2')
        self.assertEqual(event.compose.qr, '1')
        self.assertEqual(event.compose.spin, '5')
        self.assertEqual(event.compose.date, '20200811')
        self.assertEqual(event.compose.product, 'Supp')
        self.assertEqual(event.compose.parent_product, 'RHEL')
        self.assertEqual(event.compose.parent_version, '9.2.1')
        self.assertTrue(event.compose.nightly)
        self.assertTrue(event.compose.layered)
        self.assertEqual(event.compose.location, 'http://example.com/here/Supp-9.2.1-RHEL-8-20200811.n.5')

    def test_rhel_overrides(self):
        event = EventFactory.make(CliFactory.parse('compose', ['RHEL-8.3.0-20200701.2',
                                                               '--product=Test',
                                                               '--version=1.3.2',
                                                               '--location=test/location',
                                                               '--nightly=1',
                                                               '--layered=true',
                                                               '--parent-product=TEST',
                                                               '--parent-version=7.2.0'])[1])
        self.assertEqual(event.compose.id, 'RHEL-8.3.0-20200701.2')
        self.assertEqual(event.compose.version, '1.3.2')
        self.assertEqual(event.compose.major, '1')
        self.assertEqual(event.compose.minor, '3')
        self.assertEqual(event.compose.qr, '2')
        self.assertEqual(event.compose.spin, '2')
        self.assertEqual(event.compose.date, '20200701')
        self.assertEqual(event.compose.product, 'Test')
        self.assertEqual(event.compose.parent_product, 'TEST')
        self.assertEqual(event.compose.parent_version, '7.2.0')
        self.assertTrue(event.compose.nightly)
        self.assertTrue(event.compose.layered)
        self.assertEqual(event.compose.location, 'test/location')

    def test_rhel_overrides_version(self):
        event = EventFactory.make(CliFactory.parse('compose', ['RHEL-8.3.0-20200701.2',
                                                               '--version=ahoj',
                                                               '--major=10',
                                                               '--minor=9',
                                                               '--qr=8'])[1])
        self.assertEqual(event.compose.id, 'RHEL-8.3.0-20200701.2')
        self.assertEqual(event.compose.version, 'ahoj')
        self.assertEqual(event.compose.major, '10')
        self.assertEqual(event.compose.minor, '9')
        self.assertEqual(event.compose.qr, '8')

    def test_supp_overrides(self):
        event = EventFactory.make(CliFactory.parse('compose', ['Supp-9.2.1-RHEL-8-20200811.n.5',
                                                               '--product=Test',
                                                               '--version=1.3.2',
                                                               '--location=test/location',
                                                               '--nightly=no',
                                                               '--layered=no',
                                                               '--parent-product=TEST',
                                                               '--parent-version=7.2.0'])[1])
        self.assertEqual(event.compose.id, 'Supp-9.2.1-RHEL-8-20200811.n.5')
        self.assertEqual(event.compose.version, '1.3.2')
        self.assertEqual(event.compose.major, '1')
        self.assertEqual(event.compose.minor, '3')
        self.assertEqual(event.compose.qr, '2')
        self.assertEqual(event.compose.spin, '5')
        self.assertEqual(event.compose.date, '20200811')
        self.assertEqual(event.compose.product, 'Test')
        self.assertEqual(event.compose.parent_product, 'TEST')
        self.assertEqual(event.compose.parent_version, '7.2.0')
        self.assertFalse(event.compose.nightly)
        self.assertFalse(event.compose.layered)
        self.assertEqual(event.compose.location, 'test/location')

    def test_event_type(self):
        event = EventFactory.make(CliFactory.parse('compose', ['RHEL-8.3.0-20200701.2'])[1])
        self.assertEqual(event.type, 'compose')

    def test_custom_event_type(self):
        event = EventFactory.make(CliFactory.parse('compose', ['RHEL-8.3.0-20200701.2', '--event-type', 'compose.foo.bar'])[1])
        self.assertEqual(event.type, 'compose.foo.bar')

    def test_str_label(self):
        event = EventFactory.make(CliFactory.parse('compose', ['RHEL-8.3.0-20200701.2', '--event-type', 'compose.foo.bar.baz'])[1])
        self.assertEqual(str(event), 'RHEL-8.3.0-20200701.2 (Hello) baz')

    def test_str_nolabel(self):
        event = EventFactory.make(CliFactory.parse('compose', ['RHEL-8.3.0-20200701.n.2', '--event-type', 'compose.foo.bar.baz'])[1])
        self.assertEqual(str(event), 'RHEL-8.3.0-20200701.n.2 baz')
