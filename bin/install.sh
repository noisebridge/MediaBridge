#! /usr/bin/env bash

# This puts python packages where VSCode expects
# to find them by default, in .venv,
# and it does so very quickly.
# It offers control over which interpreter we use.
#
# usage: bin/install.sh $(python --version | cut -d' ' -f2)

# Specifying interpreter version is optional.
INTERPRETER=${1:-3.12}

set -e
source bin/util.sh

which uv ||
    curl -LsSf https://astral.sh/uv/install.sh | sh

test -d .venv ||
    uv venv --python=python${INTERPRETER}
set +x
source .venv/bin/activate
set -x

REQ=/tmp/requirements.txt
LCK=/tmp/requirements.lock
test -r ${REQ} || {
    env PIPENV_IGNORE_VIRTUALENVS=1 pipenv lock
    env PIPENV_IGNORE_VIRTUALENVS=1 pipenv requirements --dev |
        sed 's/; python_version .*//' > ${REQ}
}
sort -u -o ${REQ}{,}

uv pip compile --upgrade --quiet ${REQ} -o ${LCK}
uv pip install -r ${LCK}
