#!/usr/bin/python3

import logging
import unittest

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename="test_debug.log")
    loader = unittest.TestLoader()
    # just use default discover values for pattern and start_dir
    tests = loader.discover(pattern="test*.py", start_dir=".")
    runner = unittest.runner.TextTestRunner(verbosity=2)
    runner.run(tests)
