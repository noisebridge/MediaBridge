#! /usr/bin/env bash

set -x

# approximate elapsed times are
# buildx: 5 minutes (longer for initial downloads + caching)
# mb init: 4 minutes
# mb load: 5 minutes

docker buildx build -t media-bridge-image . && printf '\n\n'

docker rm -f media-bridge  2> /dev/null

docker run --name media-bridge -t media-bridge-image  bash -c "
    time pipenv run mb init &&
    time pipenv run mb load
"
