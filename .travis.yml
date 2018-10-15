language: python
matrix:
  allow_failures:
    - os: osx
  include:
    - os: linux
      python: 2.7
      cache: pip
      env: TOXENV=py27
    - os: osx
      osx_image: xcode9.3
      language: generic
      cache: pip
      sudo: required
      env: TOXENV=py27
    - os: linux
      python: 3.6
      cache: pip
      env: TOXENV=py36
    - os: osx
      language: generic
      cache: pip
      sudo: required
      env: TOXENV=py36
install:
  - if [ "$TRAVIS_OS_NAME" == "osx" ] && [ "$TOXENV" == "py27" ]; then
      sudo -H pip2 install -r requirements.txt;
    elif [ "$TRAVIS_OS_NAME" == "osx" ] && [ "$TOXENV" == "py36" ]; then
      sudo -H pip3 install -r requirements.txt;
    else
      pip install -r requirements.txt;
    fi
script:
  - cd $TRAVIS_BUILD_DIR/
  - flake8 --select E,W --max-line-length=140 --ignore E722 jarviscli/
  - cd jarviscli/
  - if [ "$TRAVIS_OS_NAME" == "osx" ] && [ "$TOXENV" == "py27" ]; then
      python2 -m unittest discover;
    elif [ "$TRAVIS_OS_NAME" == "osx" ] && [ "$TOXENV" == "py36" ]; then
      python3 -m unittest discover;
    else
      python -m unittest discover;
    fi
