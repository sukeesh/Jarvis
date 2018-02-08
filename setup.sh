#!/bin/bash
read -n 1 -p "Specify python version(2/3)(Default-3)" answer
echo ""
case ${answer:0:1} in
2 )
    echo "Selected python version 2"
;;
* )
    echo "Selected python version 3"
;;
esac

UNAME=$(uname -s)

jarvispath=$PWD

touch jarvis
chmod +rwx jarvis

exec 3<> jarvis

    echo "#!/bin/bash" >&3

    if [[ "$UNAME" == "Darwin" ]]; then
      echo ". $jarvispath/env/bin/activate" >&3
      
      case ${answer:0:1} in
      2 )
          echo "python $jarvispath/jarviscli/" >&3
      ;;
      * )
          echo "python3 $jarvispath/jarviscli/" >&3
      ;;
      esac

    else
      echo "source $jarvispath/env/bin/activate" >&3
      echo "python $jarvispath/jarviscli/" >&3
    fi

exec 3>&-

sudo mv jarvis /usr/local/bin/jarvis

#MacOS
if [[ "$UNAME" == "Darwin" ]]; then
  brew install ffmpeg
  brew install openssl
  brew install phantomjs
  case ${answer:0:1} in
    2 )
        virtualenv env --python=python2.7
        . env/bin/activate
        pip install -r requirements.txt
    ;;
    * )
        virtualenv env --python=python3.6
        . env/bin/activate
        pip3 install -r requirements.txt
    ;;
  esac
  exit 0
fi

install_phantomjs()
{
  cd /usr/local/share
  sudo wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
  sudo tar xjf phantomjs-2.1.1-linux-x86_64.tar.bz2
  sudo ln -s /usr/local/share/phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/share/phantomjs
  sudo ln -s /usr/local/share/phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/phantomjs
  sudo ln -s /usr/local/share/phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/bin/phantomjs
  cd $jarvispath
}

# Fedora based (>=22)
if [[ -f "/etc/dnf/dnf.conf" ]]; then
  sudo dnf install -y ffmpeg python-pip python-dbus notify-python
  # chromedriver-install
  wget https://chromedriver.storage.googleapis.com/2.32/chromedriver_linux64.zip
  unzip chromedriver_linux64_2.3.zip
  sudo cp chromedriver /usr/bin/chromedriver
  sudo chown root /usr/bin/chromedriver
  sudo chmod 755 /usr/bin/chromedriver
  if [ "$CHECK_PHANTOMJS" == "2.1.1" ]; then
    echo "PhantomJS is installed"
  else
    install_phantomjs
  fi

# Debian based
elif [[ -f "/etc/apt/sources.list" ]]; then
  sudo apt-get install ffmpeg python-imdbpy python-notify2 python3-dbus
  sudo apt-get install python-dbus python-dbus-dev libssl-dev libffi-dev libdbus-1-dev libdbus-glib-1-dev
  sudo apt-get install chromium-chromedriver
  sudo apt-get install build-essential chrpath libssl-dev libxft-dev libfreetype6-dev libfreetype6 libfontconfig1-dev libfontconfig1
  if [ "$CHECK_PHANTOMJS" == "2.1.1" ]; then
    echo "PhantomJs is installed"
  else
    install_phantomjs
  fi

# Arch based
elif [[ -f "/etc/pacman.conf" ]]; then
  sudo pacman -S --noconfirm ffmpeg openssl libffi python2-pip python-pip espeak
  if [ "$CHECK_PHANTOMJS" == "2.1.1" ]; then
    echo "PhantomJs is installed"
  else
    install_phantomjs
  fi

else
  echo "Operating system not supported"
  exit 1
fi

case ${answer:0:1} in
  2 )
      virtualenv env --python=python2.7
  ;;
  * )
      virtualenv env --python=python3.6
  ;;
esac

source env/bin/activate
pip install -r requirements.txt
pip install dbus-python
