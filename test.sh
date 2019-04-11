#!/bin/bash

source env/bin/activate
echo ""
echo "checking for linting errors"
flake8 --select E,W --max-line-length=140 --ignore E722 jarviscli/
echo "lint errors checked"
echo ""
cd jarviscli/
echo "checking for unit test"
python -m unittest discover
echo "unit tests checked"
echo ""