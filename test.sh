#!/usr/bin/env bash
set -ex

pipenv run python -m pytest tests/
pipenv run mypy --ignore-missing-imports --strict-optional --check-untyped-defs talepy/ tests/
pipenv run flake8 talepy tests
pipenv run isort --recursive --check-only talepy tests
