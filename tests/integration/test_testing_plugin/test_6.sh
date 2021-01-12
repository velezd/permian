setup() {
    echo "Verifies execution of workflows with logs"
    TEST_REPORT_DIR=$(mktemp -d)
    TEST_LOGS_DIR=$(mktemp -d)
}

test() {
    PIPELINEPLUGINS_ENABLE=test ./pipeline test -o "library.defaultCaseConfigMergeMethod=extension" \
                                                -o "library.directPath=tests/test_library" \
                                                -o "testingPlugin.reportSenderDirectory=$TEST_REPORT_DIR" \
                                                -o "workflows.local_logs_dir=$TEST_LOGS_DIR" \
                                                --tp 'testing plugin plan 8'

    #cp -r $TEST_REPORT_DIR $(dirname ${BASH_SOURCE[0]})/test_6_result   # update expected result
    #cp -r $TEST_LOGS_DIR $(dirname ${BASH_SOURCE[0]})/test_6_logs   # update expected result
    diff -Naur $(dirname ${BASH_SOURCE[0]})/test_6_result $TEST_REPORT_DIR &&
    diff -Naur $(dirname ${BASH_SOURCE[0]})/test_6_logs $TEST_LOGS_DIR
}

cleanup() {
    rm -rf $TEST_REPORT_DIR
    rm -rf $TEST_LOGS_DIR
}
