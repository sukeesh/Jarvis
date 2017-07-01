#!/usr/bin/sh

OS=$(lsb_release -si)
if [[ "$OS" == "Fedora" ]]; then
  sudo dnf install ffmpeg
  sudo dnf install notify-python -y
  sudo -H pip install -r requirements.txt
  sudo dnf install python-dbus -y
else
  sudo apt-get install ffmpeg
  sudo apt-get install python-notify2
  sudo -H pip install -r requirements.txt
fi
