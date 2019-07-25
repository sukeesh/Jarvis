#!/bin/bash
# fail on error!
set -euo pipefail

# check virtualenv exists
if ! which "virtualenv" 2>/dev/null >/dev/null; then
    echo "Please install virtualenv!"
    echo ""
    echo "https://github.com/pypa/virtualenv"
    echo ""
    echo "For Example on Ubuntu you could do > [sudo] apt install virtualenv"
    echo "Or use Pip: > [sudo] pip install virtualenv"
    exit -1
fi

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
          echo "python $jarvispath/jarviscli/ \$*" >&3
      ;;
      * )
          echo "python3 $jarvispath/jarviscli/ \$*" >&3
      ;;
      esac

    else
      echo "source $jarvispath/env/bin/activate" >&3
      echo "python $jarvispath/jarviscli/ \$*" >&3
    fi

exec 3>&-

case ${answer:0:1} in
  2 )
      virtualenv env --python=python2
      python_version=py2
  ;;
  * )
      virtualenv env --python=python3
      python_version=py3
  ;;
esac

VIRTUAL_ENV_DISABLE_PROMPT=true source env/bin/activate

# base requirements
pip install --upgrade -r requirements.txt

# wordnet
python -m nltk.downloader -d jarviscli/data/nltk wordnet

# voice control requirements
error=false
pip install --upgrade -r requirements_voice_control.txt 2> /dev/null || error=true
if $error; then
    error=false
    python installpyaudio.py $python_version || error=true

    if $error; then
        echo
        echo
        echo "Installation of requirements for voice control failed!"
        echo "Don't worry, Jarvis will work anyway. However if you need voice control, re-run this setup."
    else
        pip install --upgrade -r requirements_voice_control.txt
    fi
fi
sudo cp jarvis /usr/local/bin
