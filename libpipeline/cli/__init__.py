"""

"""

import sys
import os

from ..pipeline import run_pipeline
from .factory import CliFactory
from . import builtin

def main(*raw_args):
    if not raw_args:
        raw_args = sys.argv
    command_name, *args = raw_args
    filename = os.path.basename(command_name)
    options, event_spec = CliFactory.parse(filename, args)
    result = run_pipeline(event_spec, options.config, options.override)
    sys.exit(result)
