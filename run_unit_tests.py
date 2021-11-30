#!/usr/bin/python3

import logging
import unittest
import sys
import os

if __name__ == "__main__":
    # Run unittests also for external plugins
    plugins_path = os.environ.get('PIPELINEPLUGINS_PATH', '')
    plugins_dirs = set(plugins_path.split(':')) if plugins_path != '' else set()

    logging.basicConfig(level=logging.DEBUG, filename="test_debug.log")
    loader = unittest.TestLoader()

    tests = loader.discover(pattern="test*.py", start_dir=".")
    for dir in plugins_dirs:
        tests += loader.discover(pattern="test*.py", start_dir=dir)

    runner = unittest.runner.TextTestRunner(verbosity=1)
    result = runner.run(tests)
    if not result.wasSuccessful():
        sys.exit(2)
