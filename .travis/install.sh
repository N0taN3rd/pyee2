#!/usr/bin/env bash
set -e

pip install --upgrade pip
pip install --upgrade setuptools
pip install --upgrade -r dev-requirements.txt
python setup.py -q install
