from ...cli.factory import CliFactory

def register_command_parser(name, parse_function=None):
    """
    Redirects to cli.factory.CliFactory.register_command

    TBD
    """
    return CliFactory.register_command(name, parse_function)


def register_command_args_extension(extension):
    """
    Redirects to cli.factory.CliFactory.register_argparser_extension

    TBD
    """
    return CliFactory.register_argparser_extension(extension)
