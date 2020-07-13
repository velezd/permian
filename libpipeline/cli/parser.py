import re
import argparse

def base_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--override', '-o',
        action=OverrideCallback,
        type=Override,
        help='Override configuration option. It has to be provided in format: section.option=value',
    )
    parser.add_argument(
        '--config', '-c',
        action='append',
        help='',
    )
    return parser

class Override():
    """
    Parse override option provided in form section.option=value where the
    leftmost dot is considered and the leftmost equal sign (after the first
    dot) is considered.
    """
    expr = re.compile(r'^(?P<section>[^.]+)\.(?P<option>[^=]+)=(?P<value>.*)$')
    def __init__(self, value):
        mo = self.expr.match(value)
        if mo is None:
            raise argparse.ArgumentTypeError('Value of incorrect format was provided: "%s", expected value in format: "section.option=value"' % value)
        self.section = mo.group('section')
        self.option = mo.group('option')
        self.value = mo.group('value')

class OverrideCallback(argparse.Action):
    """
    Merge Overrides into one dict structure. If section or option doesn't exist
    create them. The last value of the same section.option wins.
    """
    def __init__(self, option_strings, dest, nargs=None, const=None, default=None, type=None, choices=None, required=False, help=None, metavar=None):
        if default is None:
            default = {}
        super().__init__(option_strings, dest, nargs, const, default, type, choices, required, help, metavar)
    
    def __call__(self, parser, namespace, values, option_string):
        dest = getattr(namespace, self.dest)
        if values.section not in dest:
            dest[values.section] = {}
        dest[values.section][values.option] = values.value