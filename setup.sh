#!/bin/bash
cd $(dirname $0)

if python --version; then
	python installer
elif python3 --version; then
	python3 installer
elif python2 --version; then
	python2 installer
else
	echo "Could not find Python installation"
fi
