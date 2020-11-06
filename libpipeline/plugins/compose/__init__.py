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
    id_regex = re.compile(r'(?P<product>\w+)-(?P<version>(?P<major>\d)(\.(?P<minor>\d))?(\.(?P<qr>\d))?)(-(?P<parent>\w+)-\d)?-(?P<date>\d+)(.(?P<nightly>n))?\.(?P<spin>\d)')

    def __init__(self, event_type, payload, other_data):
        super().__init__(event_type, payload, other_data)
        self._matches = re.match(self.id_regex, self.payload['id'])

    @property
    def compose_id(self):
        return self.payload['id']

    @property
    @payload_override('version')
    def compose_version(self):
        return self._matches.group('version')

    @property
    @payload_override('major')
    def compose_major(self):
        return self.compose_version.split('.')[0]

    @property
    @payload_override('minor')
    def compose_minor(self):
        try:
            return self.compose_version.split('.')[1]
        except IndexError:
            return None

    @property
    @payload_override('qr')
    def compose_qr(self):
        try:
            return self.compose_version.split('.')[2]
        except IndexError:
            return None

    @property
    def compose_spin(self):
        return self._matches.group('spin')
    
    @property
    def compose_date(self):
        return self._matches.group('date')

    @property
    @payload_override('product')
    def compose_product(self):
        return self._matches.group('product')

    @property
    @payload_override('parent_product')
    def compose_parent_product(self):
        return self._matches.group('parent')

    @property
    @payload_override('parent_version')
    def compose_parent_version(self):
        if self.compose_parent_product is not None:
            return self.compose_version

    @property
    @payload_override('nightly')
    def is_nightly(self):
        try:
            with urllib.request.urlopen(self.settings.get('compose', 'location_nightly_attr') % self.payload['id']) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as excp:
            raise Exception('Could not find compose with ID %s via %s, error %s' % (self.payload['id'], self.settings.get('compose', 'location_nightly_attr'), excp.code))

    @property
    @payload_override('layered')
    def is_layered(self):
        return self._matches.group('product').lower() == 'supp'

    @property
    @payload_override('location')
    def compose_location(self):
        try:
            with urllib.request.urlopen(self.settings.get('compose', 'location') % self.payload['id']) as response:
                return response.geturl()
        except urllib.error.HTTPError as excp:
            raise Exception('Could not find compose with ID %s via %s, error %s' % (self.payload['id'], self.settings.get('compose', 'location'), excp.code))

    def __str__(self):
        return f"Compose {self.compose_id}"

    @property
    @payload_override('location_http')
    def compose_location_http(self):
        return ''

    @property
    @payload_override('available_in')
    def compose_available_in(self):
        return []

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

    return options, json.dumps({'type': 'compose', 'payload': options.payload})
