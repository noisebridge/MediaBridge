#! /usr/bin/env bash

# usage: bin/coverage.sh

set -e
source bin/util.sh

ENV="env PYTHONPATH=.:../..:${PYTHONPATH}"

coverage erase
${ENV} coverage run -p -m pytest -v
# It's unclear where files like mv_0000002.txt come from. Unable to reproduce.
# ${ENV} coverage run -p mediabridge/data_processing/interaction_matrix.py
coverage run -p mediabridge/definitions.py 2> /dev/null || true
coverage run -p -m mediabridge.definitions
coverage run -p -m unittest mediabridge/*/*_test.py
coverage combine --quiet
coverage html
coverage report

cat <<EOF
View the coverage report in a web browser:
open htmlcov/index.html
EOF
