import argparse

from ..exceptions import UnknownCommandError
from .parser import base_argparser

class CliFactory():
    """
    Manage and run commands (parsers).
    """
    commands = {}
    extensions = []

    @classmethod
    def register_command(cls, name, parse_function=None):
        """
        Define command by name and associate function which will do the
        parsing.

        The parse function must accept following arguments:

          * base_parser - Parser with common pipeline options which should be extended with additional arguments the command needs
          * args - CLI arguments that should be parsed

        The parse function must return ``(options, event_spec)`` tuple where
        the options are return value of argparse.ArgumentParser.parse_args and
        event_spec is json encoded event that will be processed by the pipeline.

        :param name: Command name for which the parser should be used
        :type name: str
        :param parse_function: Parser function to associate to the command. Provide this argument if not used as decorator.
        :type parse_function: callable, optional
        :return: When used as decorator, the unmodified function which is decorated is returned. When the parse_function is provided, the unmodified parse_function itself is returned.
        :rtype: callable
        """
        def decorator(func):
            # TODO: check func signature
            cls.commands[name] = func
            return func
        if parse_function is not None:
            return decorator(parse_function)
        return decorator

    @classmethod
    def parse(cls, name, args, base_parser=None):
        """
        Run the parser function associated with given name and pass the args
        and base_parser to it.

        :param name: Command name that should be executed
        :type name: str
        :param args: CLI arguments that should be parsed
        :type args: list
        :param base_parser: Parser that should be provided to the command parse function as base parser. If not provided, the default common pipeline parser is used. This should not be commonly used though and it's dedicated for special purposes.
        :type base_parser: argparse.ArgumentParser, optional
        :return: (options, event_spec) Parsed arguments and json encoded pipeline event specification.
        :rtype: (argparse.Namespace, str)
        """
        if base_parser is None:
            base_parser = cls.apply_extensions(base_argparser())
        parser = cls.commands.get(name, cls.commands[None])
        return parser(base_parser, args)

    @classmethod
    def known_commands(cls, excludes=(None,)):
        """
        Provide list of currently known commands excluding the ones provided
        in excludes.

        The main purpose of this method is to provide list of commands which
        can be used when running the pipeline directly providing command name
        which should be executed.
        """
        return [ cmd for cmd in cls.commands if cmd not in excludes ]

    @classmethod
    def register_argparser_extension(cls, extension):
        """
        Register function which extends basic argparse providing common CLI
        arguments which are available for all commands. Use this with caution
        as it's very easy to collide with arguments which could be defined by
        commands. The other reason why this should be limited is that it's very
        easy to add a common option which in facts has effect only on some
        commands and such extension should be limited to only those commands
        and not added using this mechanism.

        :param extension:
        :type extension:
        """
        # TODO: check signature of apply_extensions
        cls.extensions.append(extension)

    @classmethod
    def apply_extensions(cls, parser):
        """
        Apply all registered argparser extensions to the provided parser.

        :param parser: Parser which should be extended with new parameters
        :type parser: argparse.ArgumentParser
        :raises Extension: When extension doesn't return valid parser. TODO: use custom exception
        """
        for extension in cls.extensions:
            extended = extension(parser)
            if not isinstance(extended, argparse.ArgumentParser):
                # TODO: Use custom exception
                raise Exception('Attempted to apply malfunctioning CLI extension: %r' % extension)
            parser = extended
        return parser
