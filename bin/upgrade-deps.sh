#! /usr/bin/env bash

export PIPENV_IGNORE_VIRTUALENVS=1

LOG=/tmp/mediabridge-packages.txt

set -e -x
pipenv run pip freeze  > "${LOG}"~

pipenv upgrade --dev
pipenv sync    --dev

pipenv run pip freeze  > "${LOG}"
diff -u "${LOG}"{~,}
