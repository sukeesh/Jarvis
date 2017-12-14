#!/bin/bash

if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
    # Install some custom requirements on OS X
    # e.g. brew install pyenv-virtualenv
    sudo easy_install pip
fi