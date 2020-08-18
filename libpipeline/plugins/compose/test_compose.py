import unittest
import re
from unittest.mock import patch

from libpipeline.cli.factory import CliFactory
from libpipeline.events.factory import EventFactory

class MockComposeResponse():
    def __init__(self, url):
        self.url = url
    def read(self):
        if self.url.endswith('/attr/nightly'):
            match = re.match(r'http://example\.com/compose/.+\.n\..+', self.url)
            if match:
                return 'true'
            else:
                return 'false'
        return ''
    def geturl(self):
        return self.url.replace('example.com/compose', 'example.com/here')

class MockUrlopen():
    def __init__(self, url):
        self.url = url
    def __enter__(self):
        return MockComposeResponse(self.url)
    def __exit__(self, type, value, traceback):
        pass

class TestEventCompose(unittest.TestCase):
    @patch('urllib.request.urlopen', new=MockUrlopen)
    def test_rhel_idonly(self):
        event = EventFactory.make(CliFactory.parse('compose', ['RHEL-8.3.0-20200701.2'])[1])
        self.assertEqual(event.compose_id, 'RHEL-8.3.0-20200701.2')
        self.assertEqual(event.compose_version, '8.3.0')
        self.assertEqual(event.compose_major, '8')
        self.assertEqual(event.compose_minor, '3')
        self.assertEqual(event.compose_qr, '0')
        self.assertEqual(event.compose_spin, '2')
        self.assertEqual(event.compose_date, '20200701')
        self.assertEqual(event.compose_product, 'RHEL')
        self.assertIsNone(event.compose_parent_product)
        self.assertIsNone(event.compose_parent_version)
        self.assertFalse(event.is_nightly)
        self.assertFalse(event.is_layered)
        self.assertEqual(event.compose_location, 'http://example.com/here/RHEL-8.3.0-20200701.2')

    @patch('urllib.request.urlopen', new=MockUrlopen)
    def test_supp_idonly(self):
        event = EventFactory.make(CliFactory.parse('compose', ['Supp-9.2.1-RHEL-8-20200811.n.5'])[1])
        self.assertEqual(event.compose_id, 'Supp-9.2.1-RHEL-8-20200811.n.5')
        self.assertEqual(event.compose_version, '9.2.1')
        self.assertEqual(event.compose_major, '9')
        self.assertEqual(event.compose_minor, '2')
        self.assertEqual(event.compose_qr, '1')
        self.assertEqual(event.compose_spin, '5')
        self.assertEqual(event.compose_date, '20200811')
        self.assertEqual(event.compose_product, 'Supp')
        self.assertEqual(event.compose_parent_product, 'RHEL')
        self.assertEqual(event.compose_parent_version, '9.2.1')
        self.assertTrue(event.is_nightly)
        self.assertTrue(event.is_layered)
        self.assertEqual(event.compose_location, 'http://example.com/here/Supp-9.2.1-RHEL-8-20200811.n.5')

    @patch('urllib.request.urlopen', new=MockUrlopen)
    def test_rhel_overrides(self):
        event = EventFactory.make(CliFactory.parse('compose', ['RHEL-8.3.0-20200701.2',
                                                               '--product=Test',
                                                               '--version=1.3.2',
                                                               '--location=test/location',
                                                               '--nightly=1',
                                                               '--layered=true',
                                                               '--parent-product=TEST',
                                                               '--parent-version=7.2.0'])[1])
        self.assertEqual(event.compose_id, 'RHEL-8.3.0-20200701.2')
        self.assertEqual(event.compose_version, '1.3.2')
        self.assertEqual(event.compose_major, '1')
        self.assertEqual(event.compose_minor, '3')
        self.assertEqual(event.compose_qr, '2')
        self.assertEqual(event.compose_spin, '2')
        self.assertEqual(event.compose_date, '20200701')
        self.assertEqual(event.compose_product, 'Test')
        self.assertEqual(event.compose_parent_product, 'TEST')
        self.assertEqual(event.compose_parent_version, '7.2.0')
        self.assertTrue(event.is_nightly)
        self.assertTrue(event.is_layered)
        self.assertEqual(event.compose_location, 'test/location')

    @patch('urllib.request.urlopen', new=MockUrlopen)
    def test_rhel_overrides_version(self):
        event = EventFactory.make(CliFactory.parse('compose', ['RHEL-8.3.0-20200701.2',
                                                               '--version=ahoj',
                                                               '--major=10',
                                                               '--minor=9',
                                                               '--qr=8'])[1])
        self.assertEqual(event.compose_id, 'RHEL-8.3.0-20200701.2')
        self.assertEqual(event.compose_version, 'ahoj')
        self.assertEqual(event.compose_major, '10')
        self.assertEqual(event.compose_minor, '9')
        self.assertEqual(event.compose_qr, '8')

    @patch('urllib.request.urlopen', new=MockUrlopen)
    def test_supp_overrides(self):
        event = EventFactory.make(CliFactory.parse('compose', ['Supp-9.2.1-RHEL-8-20200811.n.5',
                                                               '--product=Test',
                                                               '--version=1.3.2',
                                                               '--location=test/location',
                                                               '--nightly=no',
                                                               '--layered=no',
                                                               '--parent-product=TEST',
                                                               '--parent-version=7.2.0'])[1])
        self.assertEqual(event.compose_id, 'Supp-9.2.1-RHEL-8-20200811.n.5')
        self.assertEqual(event.compose_version, '1.3.2')
        self.assertEqual(event.compose_major, '1')
        self.assertEqual(event.compose_minor, '3')
        self.assertEqual(event.compose_qr, '2')
        self.assertEqual(event.compose_spin, '5')
        self.assertEqual(event.compose_date, '20200811')
        self.assertEqual(event.compose_product, 'Test')
        self.assertEqual(event.compose_parent_product, 'TEST')
        self.assertEqual(event.compose_parent_version, '7.2.0')
        self.assertFalse(event.is_nightly)
        self.assertFalse(event.is_layered)
        self.assertEqual(event.compose_location, 'test/location')
