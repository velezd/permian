#!/usr/bin/python3

import logging
import unittest
import sys

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename="test_debug.log")
    loader = unittest.TestLoader()
    # just use default discover values for pattern and start_dir
    tests = loader.discover(pattern="test*.py", start_dir=".")
    runner = unittest.runner.TextTestRunner(verbosity=1)
    result = runner.run(tests)
    if not result.wasSuccessful():
        sys.exit(2)
