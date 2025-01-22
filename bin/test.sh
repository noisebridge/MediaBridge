#! /usr/bin/env bash

# usage: bin/test.sh

set -e
source bin/util.sh

${ENV} python -m unittest discover -p '*_test.py'

${ENV} pytest
