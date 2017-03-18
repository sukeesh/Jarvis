#! /bin/bash
set +x

path_to_jarvis=$(pwd)

cd $path_to_jarvis
for line in $(cat requirements.txt | cut -f1 -d"="); do sudo pip install $line; done

## Determine the default shell to add the alias

default_shell=$(finger $USER | grep 'Shell:*' | cut -f3 -d ":" | sed -e 's/[\t ]//g;/^$/d' | cut -f3 -d "/")

if [ "$default_shell" == "zsh" ]; then
  echo "alias jarvis='cd $path_to_jarvis; python jarvis'" >>~/.zshrc
elif [ "$default_shell" == "sh" ]; then
  echo "alias jarvis='cd $path_to_jarvis; python jarvis'" >>~/.bashrc
fi


