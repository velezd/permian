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
    def parse(cls, name, args):
        parser = cls.commands.get(name, cls.commands[None])
        return parser(base_argparser(), args)
