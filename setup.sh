#!/bin/bash
cd $(dirname $0)

if python --version &> /dev/null; then
	python installer
elif python3 --version &> /dev/null; then
	python3 installer
elif python2 --version &> /dev/null; then
	python2 installer
else
	echo "Could not find Python installation"
fi
