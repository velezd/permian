"""
cli package handles execution of the pipeline from commandline. This package
focuses on parsing of cmdline arguments and executing the pipeline with
desired parameters.

It's possible to extend the CLI in plugins by introducing new commands.
The commands have associated parser function which provides parsed options
and event which the pipeline should react on. For more information see
CliFactory class.
"""

import sys
import os
import logging

from .. import plugins
from ..pipeline import run_pipeline
from .factory import CliFactory
from . import builtin

def main(*raw_args):
    """
    Main pipeline function which should be called when the pipeline is executed
    from CLI. The command name is detected based on the first argument (name of
    the file from which the pipeline is executed) and corresponding command
    parser is used for event generation and option parsing.

    Custom CLI arguments can be optionally provided as \*args. If those are not
    provided sys.argv content is used as CLI arguments.
    """
    plugins.load()
    if not raw_args:
        raw_args = sys.argv
    command_name, *args = raw_args
    filename = os.path.basename(command_name)
    options, event_spec = CliFactory.parse(filename, args)
    # TODO: Move logging_level to settings where --debug|--quiet would set override
    logging_level = logging.INFO
    if options.debug:
        logging_level = logging.DEBUG
    if options.quiet:
        logging_level = logging.WARN
    logging.basicConfig(
        level=logging_level,
        format="%(levelname)s:%(name)s(%(threadName)s):%(message)s",
    )
    logging.getLogger().setLevel(logging.ERROR)
    logging.getLogger('libpipeline').setLevel(logging_level)
    # the whole logging setup stuff should be probably moved elsewhere
    if options.generate_event:
        print(event_spec)
        sys.exit(0)
    result = run_pipeline(event_spec, options.settings, options.override)
    sys.exit(result)
