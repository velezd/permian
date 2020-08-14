.PHONY: rpms test doc

rpms:
test: test.lint test.unit test.integration
test.lint:
	pylint-3 -E libpipeline
test.unit:
	python3 -m unittest discover -v
test.integration:
	./run_integration_tests.sh
doc:
	make -C doc html
