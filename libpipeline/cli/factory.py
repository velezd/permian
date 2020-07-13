from ..exceptions import UnknownCommandError
from .parser import base_argparser

class CliFactory():
    commands = {}

    @classmethod
    def register(cls, name, parse_function=None):
        def decorator(func):
            cls.commands[name] = func
            return func
        if parse_function is not None:
            return decorator(parse_function)
        return decorator

    @classmethod
    def parse(cls, name, args, base_parser=None):
        if base_parser is None:
            base_parser = base_argparser()
        parser = cls.commands.get(name, cls.commands[None])
        return parser(base_parser, args)

    @classmethod
    def known_commands(cls, excludes=(None)):
        return [ cmd for cmd in cls.commands if cmd not in excludes ]
