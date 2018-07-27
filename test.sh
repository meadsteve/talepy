#!/usr/bin/env bash
set -ex

pipenv run python -m pytest tests/
pipenv run mypy --ignore-missing-imports --strict-optional --check-untyped-defs talepy/ tests/
pipenv run black --check talepy tests
