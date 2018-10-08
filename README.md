# Jarvis

[![Build Status](https://travis-ci.org/sukeesh/Jarvis.svg?branch=master)](https://travis-ci.org/sukeesh/Jarvis) [![Join the chat at https://gitter.im/Sukeesh_Jarvis/Lobby](https://badges.gitter.im/Sukeesh_Jarvis/Lobby.svg)](https://gitter.im/Sukeesh_Jarvis/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

A Personal Assistant for Linux and MacOS

![Jarvis](http://i.imgur.com/xZ8x9ES.jpg)

Jarvis is a simple personal assistant for Linux and MacOS which works on the terminal. He can talk to you if you enable his voice. He can tell you the weather, he can find restaurants and other places near you. He can do some great stuff for you. Stay updated about [new functionalities](NEW_FUNCTIONALITIES.md).

## Getting Started

In order to start Jarvis just clone the repository and run `./setup.sh`

Run **Jarvis** from anywhere by command `jarvis`

On Mac OS X run `source setup.sh`

You can start by typing `help` within the Jarvis command line to check what Jarvis can do for you.


## Youtube Video

[Click here](https://www.youtube.com/watch?v=PR-nxqmG3V8)

## Contributing

- PR's are accepted!!
- We follow PEP 8 guidelines. Before making a PR, make sure that your code is according to PEP8 standards.
- If you have some ideas for new features and you don't have time to implement them please open an issue with the tag new_feature
- Please don't forget to comment (document) your code

 ### How to run tests:

 Run `test.sh`
 ```bash
 ./test.sh
 ```

## How to write new commands (plugins) to extend Jarvis functionality

Create new file custom/hello_world.py

```
from plugin import plugin

@plugin()
def helloworld(jarvis, s):
    """Prints \"hello world!\""""
    jarvis.say("Hello World!")


@plugin()
def repeat(jarvis, s):
    """Repeats what you type"""
    jarvis.say(s)
```

Check it out!
```
./jarvis
Jarvis' sound is by default disabled.
In order to let Jarvis talk out loud type: enable sound
Type 'help' for a list of available actions.

~> Hi, what can I do for you?
helloworld
Hello World!
~> What can i do for you?
repeat Jarvis is cool!
jarvis is cool
```

[Click here](PLUGINS.md) to learn more about plugins.


## Authors

 **sukeesh**

See also the list of [contributors](https://github.com/sukeesh/Jarvis/graphs/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
