#!/usr/bin/env bash

shopt -s nocasematch
expected_python_path="$PWD/.venv/bin/python"
actual_python_path="$(which python)"

if [[ ! $expected_python_path = $actual_python_path ]]; then
  echo Should be run like: poetry run $0
  exit
fi

set -x
set -u
set -o pipefail

black .
isort .
pytest --cov --cov-report=term-missing --cov-report=xml:coverage.xml
mypy --install-types --non-interactive .
pylint src

