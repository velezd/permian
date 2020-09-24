setup() {
    true
}

test() {
    ./pipeline example -o library.directPath=./tests/test_library
}

cleanup() {
    true
}
