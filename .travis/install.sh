#!/usr/bin/env bash
set -e

pip install --upgrade setuptools
pip install --upgrade pip
pip install --upgrade pytest pytest-asyncio mock uvloop
python setup.py -q install
