#! /usr/bin/env bash

# usage: bin/coverage.sh

set -e
source bin/util.sh

coverage erase
coverage run -m unittest discover -p '*_test.py'
coverage html
coverage report
