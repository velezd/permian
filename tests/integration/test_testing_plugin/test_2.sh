setup() {
    echo "Verifies execution of multiple overlapping test plans where only some configurations of a TestCase are overlapping"
    TEST_REPORT_DIR=$(mktemp -d)
}

test() {
    PIPELINEPLUGINS_ENABLE=test ./pipeline test -o "library.defaultCaseConfigMergeMethod=extension" \
                                                -o "library.directPath=tests/test_library" \
                                                -o "testingPlugin.reportSenderDirectory=$TEST_REPORT_DIR" \
                                                --tp 'testing plugin plan 3' \
                                                --tp 'testing plugin plan 4'
    
    #cp -r $TEST_REPORT_DIR $(dirname ${BASH_SOURCE[0]})/test_2_result   # update expected result
    diff -r $TEST_REPORT_DIR $(dirname ${BASH_SOURCE[0]})/test_2_result
}

cleanup() {
    rm -rf $TEST_REPORT_DIR
}
