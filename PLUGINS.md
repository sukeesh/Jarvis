# Plugins

## Basic
```
from plugin import plugin

@plugin
def hello_world(jarvis, s):
    """Prints \"hello world!\""""
    jarvis.say("Hello World!")
```

Or use "callable" class:

```
from plugin import plugin

@plugin
class hello_world:
    """Prints \"hello world!\""""
    def __call__(self, jarvis, s):
        jarvis.say("Hello World!")
```


## Naming

The Class/Method name equals the Jarvis-command name.

So imagine you want to do something if user enters "laugh", do something like: ``def laugh(javis, s)`` or ``class laugh(plugin)``. And this method (or run()-method) will be called each time the user enters "laugh" in the javis prompt.

Please note:

* Case-insenstive - Jarvis commands are always lower case
* Do not use "_"
* __ means "comment" - everything beyond is ignored

So these plugins are equivalent:

* HelloWorld
* helloworld
* HelloWorld__LINUX_ONLY

But **NOT**:

* hello_world

That would mean something totally [different](PLUGINS.md#two-word-commands).


## Run-Parameter

* 1: jarvis -> instance of CmdInterpreter.JarvisAPI. You'll probably most need ``jarvis.say(text, color=None)`` to print/say stuff. If you need color, take a loot at [colorama](https://pypi.org/project/colorama/).
* 2: s -> string; what the user entered

## Location

Plugins are searched for in two locations:

* custom - for your own plugins
* jarviscli/plugins - for pre-installed plugins

It is fine to develop and test plugins in the custom-folder, but before submitting always move them to jarviscli/plugins.


## Features

Plugins may be modified using the decorators @alias, @require and @complete.

These special decorators may be used in any order or several times.

Note that @plugin always **must** be declared last.


### Alias

Example:

```
from plugin import plugin, alias


@alias("Hello", "Hi")
@plugin
def helloWorld(jarvis, s):
   (...)
```

This would alias "HelloWorld" to "Hello" and "Hi".

An Alias behaves just like copy-pasting the whole plugin with a new name.

### Require

Not all plugins are compatible with every system. To specify compatibility constraints, use the require-feature.

Plugins, which are non compatible are ignored and will not be displayed.

Current available requirements:

* Network: (True, False)
* Plattform: (plugin.LINUX, plugin.MACOS)
* Python: (plugin.PYTHON2, plugin.PYTHON3)
* Native: (any string)

Native means any native Binary in $PATH must exist. If multiple natives are specified (unlike other requirements) ALL must be fulfilled.

Example: Only support Python 3 with Linux; Require firefox and curl with active network connection.


```
from plugin import plugin, require, PYTHON3, LINUX


@require(platform=LINUX, python=PYTHON3, network=True, native=["firefox", "curl"])
@plugin
def helloWorld(jarvis, s):
    (...)
```

Special behaviour:

* If a plugin is incompabible because of missing native binary (and because of natives only), an notification shall be printed.
* If network=True is required, you won't need to try-catch requests.ConnectionError - this error is auto-cached with connection-error


### Completion

Use Completion feature (complete with TAB).

```
from plugin import plugin, complete


@complete("complete0", "complete1")
@plugin
def helloWorld(jarvis, s):
    (...)
```


### Two word commands

Take "check ram" and "check weather". Of course you could create a plugin "check" and doing something like ``if 'ram' in s``. But it's better to create two separate plugins:

```
@plugin
check_ram(jarvis, s):
    (...)


@plugin
check_weather(jarvis, s):
    (...)
```

One '_' in class- or method-names split first word from second.

Two word commands even work with alias() (but use Space instead of '_').

Note that this only works for two-word commands - there is currently nothing like "three world commands".


### Init

If a Class-Plugins has a method ``init(self, jarvis)`` this method will be called during initialisation.

```
from plugin import plugin


@plugin
class HelloWorld:
    """
    Description of Hello world
    """
    def init(self, jarvis):
        jarvis.say("INIT HelloWorld!!!")

    def require(self):
        pass

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        jarvis.say("Hello world!")
```
