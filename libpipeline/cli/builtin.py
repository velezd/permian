import sys

from .factory import CliFactory

@CliFactory.register('run_event')
def direct_event(base_parser, args):
    base_parser.add_argument('event')
    options = base_parser.parse_args(args)
    return options, options.event

@CliFactory.register('pipeline')
def pipeline_command(base_parser, args):
    """
    You are most probably not interested in this command as it's very generic
    command handler which is used only if the pipeline is executed directly
    using the ``./pipeline`` command. In this case, additional argument
    specifying the command is needed and that's the only thing this command
    handler does - additional command argument is added to the parser and
    based on the provided command, this handler starts the parsing machinery
    again but now using the provided command.

    Note that modified parser needs to be used as the command name remains
    among the arguments.

    Note that this technique (calling other parsers from the parse function)
    should be avoided.
    """
    base_parser.add_argument('command')
    options, _ = base_parser.parse_known_args(args)
    return CliFactory.parse(options.command, args, base_parser)

@CliFactory.register(None)
def unknown_command(base_parser, args):
    print('Pipeline executed with unknown command.')
    sys.exit(2)
