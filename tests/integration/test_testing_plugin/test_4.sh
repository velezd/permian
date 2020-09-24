setup() {
    echo "Verifies execution of TestPlans with single and multiple test reporting"
    TEST_REPORT_DIR=$(mktemp -d)
}

test() {
    PIPELINEPLUGINS_ENABLE=test ./pipeline test -o "library.defaultCaseConfigMergeMethod=extension" \
                                                -o "library.directPath=tests/test_library" \
                                                -o "testingPlugin.reportSenderDirectory=$TEST_REPORT_DIR" \
                                                --tp 'testing plugin plan 5' \
                                                --tp 'testing plugin plan 6'
    
    #cp -r $TEST_REPORT_DIR $(dirname ${BASH_SOURCE[0]})/test_4_result   # update expected result
    diff -r $TEST_REPORT_DIR $(dirname ${BASH_SOURCE[0]})/test_4_result
}

cleanup() {
    rm -rf $TEST_REPORT_DIR
}
