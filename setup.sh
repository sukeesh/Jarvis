#!/bin/bash

jarvispath=$PWD
touch jarvis
chmod +rwx jarvis
exec 3<> jarvis

    # Let's print some text to fd 3
    echo "#!/bin/bash" >&3
    echo "python $jarvispath/jarviscli/" >&3

# Close fd 3
exec 3>&-
sudo mv jarvis /usr/local/bin/jarvis

UNAME=$(uname -s)
if [[ "$UNAME" == "Darwin" ]]; then
  brew install ffmpeg
  brew install openssl
  virtualenv env
  . env/bin/activate
  pip install -r requirements.txt
  exit 0
fi

OS=$(lsb_release -si)
if [[ "$OS" == "Fedora" ]]; then
  sudo dnf install ffmpeg
  sudo dnf install notify-python -y
  sudo -H pip install -r requirements.txt
  sudo dnf install python-dbus -y
  # chromedriver-install
  wget https://chromedriver.storage.googleapis.com/2.32/chromedriver_linux64.zip
  unzip chromedriver_linux64_2.3.zip
  sudo cp chromedriver /usr/bin/chromedriver
  sudo chown root /usr/bin/chromedriver
  sudo chmod 755 /usr/bin/chromedriver
elif [[ "$OS" == "Ubuntu" ]] || [[ "$OS" == "LinuxMint" ]]; then
  sudo apt-get install ffmpeg python-imdbpy python-notify2
  sudo apt-get install python-dbus libssl-dev libffi-dev
  sudo -H pip install -r requirements.txt
  sudo apt-get install chromium-chromedriver
elif [[ "$OS" == "Kali" ]]; then
  apt-get install ffmpeg
  apt-get install python-notify2
  apt-get install python-dbus
  pip install -r requirements.txt
else
  echo "Operating System not supported"
  exit 1
fi
exit 0
