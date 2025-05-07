#! /usr/bin/env bash

# usage: bin/lint.sh [--only <tool>]
set -e
source bin/util.sh

# Turn off tracing, we explicitly echo the commands below.
set +x

# Define the valid options.
OPTIONS=$(getopt --long "only:" -- "$@")

# Check if getopt was successful
if [ $? -ne 0 ]; then
  echo "Error parsing options." >&2
  exit 1
fi

# Set the positional parameters based on the parsed options
eval set -- "$OPTIONS"

only_value=""

# Loop through the options
while true; do
  case "$1" in
    --only)
      only_value="$2"
      shift 2
      ;;
    --)
      shift
      break
      ;;
    *)
      echo "Internal error!" >&2
      exit 1
      ;;
  esac
done

# If there is no value for "--only", or there is and it equals "ruff"
if [[ -x "$only_value" || "$only_value" == "ruff" ]]; then
  cmd="${ENV} ruff check ."
  echo $cmd
  $cmd
fi

# If there is no value for "--only", or there is and it equals "mypy"
if [[ -x "$only_value" || "$only_value" == "mypy" ]]; then
  cmd=${ENV} mypy --strict --show-traceback --warn-unreachable --ignore-missing-imports --no-namespace-packages --exclude=mediabridge/main.py .
  echo $cmd
  $cmd
fi

# If there is no value for "--only", or there is and it equals "pyright"
if [[ -x "$only_value" || "$only_value" == "pyright" ]]; then
  cmd=${ENV} pyright .
  echo $cmd
  $cmd
fi