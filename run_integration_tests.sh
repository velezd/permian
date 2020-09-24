#!/bin/bash -eu

NOCOLOR="$(tput -Tlinux sgr0)"
BOLD="$(tput -Tlinux bold)"
RED="$(tput -Tlinux setaf 1)"
GREEN="$(tput -Tlinux setaf 2)"

RESULT=0

for test in tests/integration/*/test_*.sh	; do
    echo "${BOLD}STARTING TEST: ${test}${NOCOLOR}"
    source ${test}
    if ! setup; then
        echo "${BOLD}TEST ${test} ${RED}SETUP ERRROR${NOCOLOR}"
        exit 2
    fi
    if ( set -exu; test ); then
        echo "${BOLD}TEST ${test} ${GREEN}PASSED${NOCOLOR}"
    else
        echo "${BOLD}TEST ${test} ${RED}FAILED${NOCOLOR}"
        RESULT=1
    fi
    if ! cleanup; then
        echo "${BOLD}TEST ${test} ${RED}CLEANUP ERRROR${NOCOLOR}"
        RESULT=3
    fi
done

exit $RESULT
