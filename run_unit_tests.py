#!/usr/bin/python3

import logging
import unittest
import sys
import os

import libpermian.plugins

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename="test_debug.log")
    loader = unittest.TestLoader()

    tests = loader.discover(pattern="test*.py", start_dir=".")
    libpermian.plugins.load()
    for plugin in list(libpermian.plugins.loaded_plugin_modules()):
        tests.addTests(loader.discover(pattern="test*.py", start_dir=plugin.__name__))

    runner = unittest.runner.TextTestRunner(verbosity=1)
    result = runner.run(tests)
    if not result.wasSuccessful():
        sys.exit(2)
