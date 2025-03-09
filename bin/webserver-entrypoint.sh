#! /usr/bin/env bash

if [ ! -d bin/ ]
then
    echo "Please run $0 from top-level."
    exit 1
fi

if [ ! -d out/ ]
then
    time (pipenv run mb init &&
          pipenv run mb load)
fi

# NB: the datasette uvicorn webserver will run until CTRL/C
pipenv run browse
