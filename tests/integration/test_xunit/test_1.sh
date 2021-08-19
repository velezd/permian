setup() {
    TEST_REPORT_DIR=$(mktemp -d)
}

test() {
    PIPELINEPLUGINS_ENABLE=test ./pipeline test -o "library.defaultCaseConfigMergeMethod=extension" \
                                                -o "library.directPath=tests/test_library" \
                                                -o "reportSenders.reporting_dir=$TEST_REPORT_DIR" \
                                                --tp 'xunit grouped testplan'

    #cp -r $TEST_REPORT_DIR $(dirname ${BASH_SOURCE[0]})/test_1_result   # update expected result
    diff -Naur $(dirname ${BASH_SOURCE[0]})/test_1_result $TEST_REPORT_DIR
}

cleanup() {
    rm -rf $TEST_REPORT_DIR
}
