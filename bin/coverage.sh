#! /usr/bin/env bash

# usage: bin/coverage.sh

set -e
source bin/util.sh

coverage erase
coverage run -m unittest mediabridge/*/*_test.py
coverage html
coverage report
