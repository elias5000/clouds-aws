#!/bin/bash
# Run this before committing changes.
# Score should be 10 and must not be lower than 9

PY_FILES=$(find src -name \*.py -not -path ./virtualenv/\* -not -path ./.vscode/\*)
pylint ${PY_FILES}
