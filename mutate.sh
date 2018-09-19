#!/usr/bin/env bash

set -ex

cosmic-ray init config.yml mutation_session
cosmic-ray exec mutation_session
cosmic-ray dump mutation_session | cr-report