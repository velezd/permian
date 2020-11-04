setup() {
    echo "Verifies execution of TestPlans with multiple test reporting with group_by and without it"
    TEST_REPORT_DIR=$(mktemp -d)
}

test() {
    PIPELINEPLUGINS_ENABLE=test ./pipeline test -o "library.defaultCaseConfigMergeMethod=extension" \
                                                -o "library.directPath=tests/test_library" \
                                                -o "testingPlugin.reportSenderDirectory=$TEST_REPORT_DIR" \
                                                --tp 'testing plugin plan 7'

    #cp -r $TEST_REPORT_DIR $(dirname ${BASH_SOURCE[0]})/test_5_result   # update expected result
    diff -Naur $(dirname ${BASH_SOURCE[0]})/test_5_result $TEST_REPORT_DIR
}

cleanup() {
    rm -rf $TEST_REPORT_DIR
}
