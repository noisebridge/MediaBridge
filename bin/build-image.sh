#! /usr/bin/env bash

set -x

# approximate elapsed times are
# buildx: 5 minutes (longer for initial downloads + caching)
# mb init: 4 minutes
# mb load: 5 minutes

docker buildx build -t media-bridge . && printf '\n\n'

docker run -t media-bridge  pipenv run mb init

docker run -t media-bridge  pipenv run mb load
