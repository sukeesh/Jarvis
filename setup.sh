#!/bin/bash

jarvispath=$PWD
touch jarvis
chmod +rwx jarvis
exec 3<> jarvis

    echo "#!/bin/bash" >&3
    echo "source $jarvispath/env/bin/activate" >&3
    echo "python $jarvispath/jarviscli/" >&3

exec 3>&-

sudo mv jarvis /usr/local/bin/jarvis

# Fedora based (>=22)
if [[ -f "/etc/dnf/dnf.conf" ]]; then
  sudo dnf install -y ffmpeg python-pip python-dbus notify-python
  # chromedriver-install
  wget https://chromedriver.storage.googleapis.com/2.32/chromedriver_linux64.zip
  unzip chromedriver_linux64_2.3.zip
  sudo cp chromedriver /usr/bin/chromedriver
  sudo chown root /usr/bin/chromedriver
  sudo chmod 755 /usr/bin/chromedriver

# Debian based
elif [[ -f "/etc/apt/sources.list" ]]; then
  sudo apt-get install ffmpeg python-pip python-imdbpy python-notify2
  sudo apt-get install python-dbus python-dbus-dev libssl-dev libffi-dev libdbus-1-dev libdbus-glib-1-dev
  sudo apt-get install chromium-chromedriver python2.7

# Arch based
elif [[ -f "/etc/pacman.conf" ]]; then
  sudo pacman -S --noconfirm ffmpeg openssl libffi python2-pip python-pip

# MacOS
UNAME=$(uname -s)
if [[ "$UNAME" == "Darwin" ]]; then
  brew install ffmpeg
  brew install openssl
  virtualenv env
  . env/bin/activate
  pip install -r requirements.txt
  exit 0
else
  echo "Operating system not supported"
  exit 1
fi

# Check if sudo is required
pip install virtualenv
if [[ "$?" -eq 2 ]]; then
  sudo pip install virtualenv
fi

virtualenv env --python=python2.7
source env/bin/activate
pip install -r requirements.txt

sudo pip install dbus-python

exit 0
