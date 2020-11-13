import json
import logging
import time
import re
import urllib.request
import urllib.error
import json

from .. import api
from ...events.base import Event, payload_override
from ...cli.parser import bool_argument, ToPayload, AppendToPayload


@api.events.register('compose')
class ComposeEvent(Event):
    def __init__(self, type, compose, **kwargs):
        super().__init__(type, compose=compose, **kwargs)

    def __str__(self):
        return f"Compose {self.compose.id}"

@api.events.register_structure('compose')
class ComposeStructure():
    id_regex = re.compile(r'(?P<product>\w+)-(?P<version>(?P<major>\d+)(\.(?P<minor>\d+))?(\.(?P<qr>\d))?)(-(?P<parent>\w+)-\d)?-(?P<date>\d+)(\.(?P<flag>.))?\.(?P<spin>\d+)')

    def __init__(self, id, product=None, version=None, major=None, minor=None, qr=None, date=None, respin=None, location=None, location_http=None, nightly=None, development=None, layered=None, parent_product=None, parent_version=None, available_in=None):
        self.id = id
        self._matches = re.match(self.id_regex, self.id)
        self.product = product or self._matches.group('product')
        self.version = version or self._matches.group('version')
        self.major = major or self.version.split('.')[0]
        self.minor = minor or self.version.split('.')[1]
        self.date = date or self._matches.group('date')
        self.spin = respin or self._matches.group('spin')
        try:
            self.qr = qr or self.version.split('.')[2]
        except IndexError:
            self.qr = None
        self._location = location
        self.location_http = location_http
        self._nightly = nightly
        self.development = development if development is not None else self._matches.group('flag') == 'd'
        self._layered = layered
        self._parent_product = parent_product
        self._parent_version = parent_version
        self.available_in = [] if available_in is None else available_in

    @property
    def location(self):
        if self._location:
            return self._location
        try:
            with urllib.request.urlopen(self.settings.get('compose', 'location') % self.id) as response:
                return response.geturl()
        except urllib.error.HTTPError as excp:
            raise Exception('Could not find compose with ID %s via %s, error %s' % (self.id, self.settings.get('compose', 'location'), excp.code))

    @property
    def nightly(self):
        if self._nightly is not None:
            return self._nightly
        try:
            with urllib.request.urlopen(self.settings.get('compose', 'location_nightly_attr') % self.id) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as excp:
            raise Exception('Could not find compose with ID %s via %s, error %s' % (self.id, self.settings.get('compose', 'location_nightly_attr'), excp.code))

    @property
    def layered(self):
        if self._layered is not None:
            return self._layered
        return self._matches.group('product').lower() == 'supp'

    @property
    def parent_product(self):
        if self._parent_product:
            return self._parent_product
        if not self.layered:
            return None
        return self._matches.group('parent')

    @property
    def parent_version(self):
        if self._parent_version:
            return self._parent_version
        if not self.layered:
            return None
        return self.version


@api.cli.register_command_parser('compose')
def compose_command(base_parser, args):
    parser = base_parser
    parser.add_argument('id', action=ToPayload,
                        help='Compose ID e.g. RHEL-8.3.0-20200701.2')
    parser.add_argument('--product', action=ToPayload,
                        help='Product name as usually appears in ID')
    parser.add_argument('--version', action=ToPayload,
                        help='Product version in format major.minor.qr, minor and qr are optional')
    parser.add_argument('--major', action=ToPayload,
                        help='Product version major part only')
    parser.add_argument('--minor', action=ToPayload,
                        help='Product version minor part only')
    parser.add_argument('--qr', action=ToPayload,
                        help='Product version quarterly release part only')
    parser.add_argument('--location', action=ToPayload,
                        help='URL to compose location')
    parser.add_argument('--nightly', type=bool_argument, action=ToPayload,
                        help='Is compose nighlty, true/false')
    parser.add_argument('--layered', type=bool_argument, action=ToPayload,
                        help='Is compose layered, true/false')
    parser.add_argument('--parent-product', action=ToPayload,
                        help='Name of parent product, for layered compose')
    parser.add_argument('--parent-version', action=ToPayload,
                        help='Version of parent product, for layered compose')
    # this is required mostly for legacy_puzzle_merger and is subject of
    # discussion in team once legacy_puzzle_merger workflow is decommisioned
    parser.add_argument('--available-in', action=AppendToPayload, default=[],
                        help='Systems in which the compose is expected to be available.')
    options = parser.parse_args(args)

    return options, json.dumps({'type': 'compose', 'compose': options.payload})
