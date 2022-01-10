#!/usr/bin/python3

import time
import sys

finish_after_number_of_tests = 999999999
time_consumed_by_test = 0


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print(f"Usage: launch-mock.py <FILE_WITH_OUTPUT> [NUMBER_OF_TESTS] [SECS_PER_TEST]")
        exit(1)

    if len(sys.argv) > 3:
        time_consumed_by_test = float(sys.argv[3])
    if len(sys.argv) > 2:
        finish_after_number_of_tests = int(sys.argv[2])
    file_with_output = sys.argv[1]

    test_is_running = False
    number_of_tests = 0
    with open(file_with_output) as f:
        for line in f:
            if line.startswith("INFO: RESULT"):
                if time_consumed_by_test:
                    time.sleep(time_consumed_by_test)
                number_of_tests += 1
            print(line.strip())
            if number_of_tests == finish_after_number_of_tests:
                break
