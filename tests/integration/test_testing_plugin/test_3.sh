setup() {
    echo "Verifies execution of multiple overlapping test plans where there's no overlap of configurations of a TestCase"
    TEST_REPORT_DIR=$(mktemp -d)
}

test() {
    PIPELINEPLUGINS_ENABLE=test ./pipeline test -o "library.defaultCaseConfigMergeMethod=extension" \
                                                -o "library.directPath=tests/test_library" \
                                                -o "testingPlugin.reportSenderDirectory=$TEST_REPORT_DIR" \
                                                --tp 'testing plugin plan 4' \
                                                --tp 'testing plugin plan 5'
    
    #cp -r $TEST_REPORT_DIR $(dirname ${BASH_SOURCE[0]})/test_3_result   # update expected result
    diff -Naur $(dirname ${BASH_SOURCE[0]})/test_3_result $TEST_REPORT_DIR
}

cleanup() {
    rm -rf $TEST_REPORT_DIR
}
