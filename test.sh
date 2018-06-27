#!/usr/bin/env bash
set -ex

pipenv run py.test tests
pipenv run mypy --ignore-missing-imports --strict-optional --check-untyped-defs talepy/
pipenv run flake8 talepy tests
pipenv run isort --recursive --check-only talepy tests
