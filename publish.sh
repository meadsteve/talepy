#!/usr/bin/env bash

set -ex

version=`pipenv run python setup.py --version`

if git tag --list | grep "v$version";
then
    echo "Version already released"
else
    pipenv run python setup.py sdist
    pipenv run twine upload dist/talepy-$version.tar.gz -r pypi
    git tag -a v$version -m "v$version"
    git push origin v$version
fi