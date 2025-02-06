#! /usr/bin/env bash

set -e
cd ../MediaBridge/mediabridge  # run scripts from top-level of the repo
# Alas, MacOS is case-insensitive, so this little dance ensures we're at repo top.
cd ..
cd ../MediaBridge

if [ -d .venv ]
then
    source .venv/bin/activate
fi

export ENV="env PYTHONPATH=.:../.."

set -x
