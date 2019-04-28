#!/usr/bin/env bash
set -ex

pipenv run mutmut run
pipenv run mutmut results
