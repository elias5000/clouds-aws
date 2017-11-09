#!/bin/bash
# little helper to setup local development environment

if [ ! -d virtualenv ]; then
  virtualenv -p python3 virtualenv
fi

source ./virtualenv/bin/activate

pip install -e .
pip install pylint pycodestyle
