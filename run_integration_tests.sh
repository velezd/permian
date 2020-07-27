#!/bin/bash

NOCOLOR="$(tput sgr0)"
BOLD="$(tput bold)"
RED="$(tput setaf 1)"
GREEN="$(tput setaf 2)"

for test in tests/integration/*/test_*.sh	; do
    echo "${BOLD}STARTING TEST: ${test}${NOCOLOR}"
    bash -exu ${test}
    if [ $? -eq 0 ]; then
        echo "${BOLD}TEST ${test} ${GREEN}PASSED${NOCOLOR}"
    else
        echo "${BOLD}TEST ${test} ${RED}FAILED${NOCOLOR}"
    fi
done
