import json

from .. import api
from ...events.base import Event

@api.events.register('demo')
class DemoEvent(Event):
    pass

@api.cli.register_command_parser('demo')
def demo_command(base_parser, args):
    from .. import test
    options = base_parser.parse_args(args)
    options.override.setdefault("shutdownDelay", {})
    options.override["shutdownDelay"]["enabled"] = True
    options.override.setdefault("library", {})
    options.override["library"]["directPath"] = "tests/test_library/demo"
    return options, json.dumps({"type": "demo"})
