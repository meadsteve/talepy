#!/usr/bin/env bash
set -ex

py.test tests
mypy --ignore-missing-imports --strict-optional --check-untyped-defs talepy/
flake8 talepy tests
isort --recursive --check-only talepy tests
