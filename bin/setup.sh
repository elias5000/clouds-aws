#!/bin/bash
# little helper to setup local development environment

if [ ! -d .virtualenv ]; then
  virtualenv -p python3 .virtualenv || exit 1
fi

source ./.virtualenv/bin/activate

pip install -e .
pip install pylint pycodestyle
