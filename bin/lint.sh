#! /usr/bin/env bash

# usage: bin/lint.sh

set -e
source bin/util.sh

${ENV} ruff check .

${ENV} mypy --strict --show-traceback --warn-unreachable --ignore-missing-imports --no-namespace-packages .

${ENV} pyright .
