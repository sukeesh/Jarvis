# Plugins

## Hello world

* Create new file custom/hello_word.py or jarviscli/packages/hello_world.py with:

```
from plugin import Plugin


class HelloWorld(Plugin):
    """
    Description of Hello world
    """
    def require(self):
        pass

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        jarvis.say("Hello world!")
```

You just created a new command HelloWorld.

Let's try out!

* run Jarvis
* Type help HelloWorld -> watch Class doc String print
* Type HelloWorld -> watch run() being executed

Few words about class-Name:

* Class-Name equals command name
* Case-insenstive
* One word: Do not use _ (unless [Two word command](PLUGINS.md#two-word-commands))
* Everything after two _ (__) is ignored


Run-Parameters:

* jarvis -> instance of CmdInterpreter.JarvisAPI. You'll probably most need say(text, color=None) to print/say stuff.
* s -> the complete command string the user entered.


## Short "Decorator" style

For small commands, there is an alternative, compact declaration style:

```
form plugin import plugin


@plugin()
def helloWorld(jarvis, s):
    """Description of Hello world"""
    jarvis.say("Hello world!")
```

Note the difference between plugin (Decorator) and Plugin (Class).

Since @plugin converts the method to a Plugin-Subclass, there is no real difference between Decorator and Class-style.

For bigger plugins (>10 lines) it is strongly recommendet to use Class-style. 



## "Advanced" Plugin Features

### Alias

"Goodbye", "Close", "Exit" - these commands should all do the same.

So that you don't have to create 3 Plugins, there is the "alias"-feature.

If you - for example - want "Hello" and "Hi" to be aliases for HelloWorld, write something like

Class-style:
```
    def alias(self):
       yield "Hello"
       yield "Hi"
```
Decorator-style:
```
from plugin import plugin, alias


@plugin()
@alias("Hello", "Hi")
def helloWorld(jarvis, s):
   (...)
```

### Require

Not all plugins are compabible with every system. To specify compbability constraints, use the require-feature.

Plugins, which are non compabible are ignored and will not be displayed.

Current available requirements:

* Network: (True, False)
* Plattform: (plugin.LINUX, plugin.MACOS)
* Python: (plugin.PYTHON2, plugin.PYTHON3)
* Native: (any string)

Native means any native Binary in $PATH must exist. If multiple natives are specified (unlike other requirements) ALL must be fullfilled.

Example: Only support Python 3 with Linux; Require firefox and curl with active network connection.

Class-style:
```
from plugin import Plugin, PYTHON3, LINUX

    def require(self):
        yield("plattform", LINUX)
        yield("python", PYTHON3)
        yield("network", True)
        yield("native", ["firefox", "curl"])
```

Decorator-style:
```
from plugin import plugin, PYTHON3, LINUX


@plugin(plattform=LINUX, python=PYTHON3, network=True, native=["firefox", "curl"])
def helloWorld(jarvis, s):
    (...)
```

Special behaviour:

* If a plugin is incompabible because of missing native binary (and because of natives only), an notification shall be printed.
* If network=True is required, you won't need to try-catch requests.ConnectionError - this error is auto-cached with connection-error


### Completion

Use Completion feature (complete with TAB).

Class-style:
```
from plugin import Plugin

    def complete(self):
        yield "complete0"
        yield "complete1"
```

Decorator-style:
```
from plugin import plugin, complete


@plugin()
@complete("complete0", "complete1")
def helloWorld(jarvis, s):
    (...)
```


### Two word commands

Take "check ram" and "check weather". It is possible to implement these in two different plugins:

```
@plugin()
check_ram(jarvis, s):
    (...)


@plugin()
check_weather(jarvis, s):
    (...)
```

One '_' in class- or method-names split first word from second.

Two word commands even work with alias() (but use Space instead of '_'):

```
from plugin import Plugin


class HelloWorld(Plugin):
    """
    Description of Hello world
    """
    def require(self):
        pass

    def complete(self):
        pass

    def alias(self):
        yield("Hello world")

    def run(self, jarvis, s):
        jarvis.say("Hello world!")
```

Will make "Hello world" available.

Note that this only works for two-word commands - there is currenlty nothing like "three world commands".
