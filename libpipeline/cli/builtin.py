import sys

from .factory import CliFactory

@CliFactory.register_command('run_event')
def direct_event(base_parser, args):
    """
    Universal command where event is provided as the first positional argument.

    This command is not meant for day to day use and its main purpose is to
    provide simple interface for direct event specification on cmdline which
    can be used for execution in Jenkins environment or for debugging purposes.
    """
    base_parser.add_argument('event')
    options = base_parser.parse_args(args)
    return options, options.event

@CliFactory.register_command('pipeline')
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
    base_parser.add_argument(
        'command',
        choices=CliFactory.known_commands((None, 'pipeline'))
    )
    options, _ = base_parser.parse_known_args(args)
    return CliFactory.parse(options.command, args, base_parser)

@CliFactory.register_command(None)
def unknown_command(base_parser, args):
    """
    Fallback command parser which is used when the pipeline is executed under
    unknown name (filename doesn't match any known command name).
    """
    print('Pipeline executed with unknown name (no corresponding command was found).')
    sys.exit(2)
