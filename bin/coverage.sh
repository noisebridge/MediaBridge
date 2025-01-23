#! /usr/bin/env bash

# usage: bin/coverage.sh

set -e
source bin/util.sh

ENV="env PYTHONPATH=.:../..:${PYTHONPATH}"

coverage erase
${ENV} coverage run -p -m pytest -v
coverage run -p mediabridge/definitions.py 2> /dev/null || true
coverage run -p -m mediabridge.definitions
coverage run -p -m unittest mediabridge/*/*_test.py
coverage combine --quiet
coverage html
coverage report
