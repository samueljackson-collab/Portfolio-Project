.PHONY: tools-test

tools-test:
	PYTHONPATH=. python -m pytest tools/dupefinder/tests
