#!/usr/bin/env bash

# Use https://github.com/clibs/entr to run the tests on any python file change
find . -name '*.py' | entr ./test.sh
