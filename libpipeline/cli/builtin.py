import sys

from .factory import CliFactory

@CliFactory.register('run_event')
def direct_event(base_parser, args):
    base_parser.add_argument('event')
    options = base_parser.parse_args(args)
    return options, options.event

@CliFactory.register(None)
def unknown_command(base_parser, args):
    print('Pipeline executed under unknown command. Please use one of the symlinks available.')
    sys.exit(2)
