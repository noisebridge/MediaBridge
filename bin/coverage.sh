#! /usr/bin/env bash

# usage: bin/coverage.sh

set -e
source bin/util.sh

ENV="env PYTHONPATH=.:../..:${PYTHONPATH}"

coverage erase
coverage run -p mediabridge/definitions.py 2> /dev/null || true
coverage run -p -m mediabridge.definitions
coverage run -p -m unittest mediabridge/*/*_test.py
${ENV} pytest --cov --cov-report=term-missing
coverage combine --quiet
coverage html
coverage report
