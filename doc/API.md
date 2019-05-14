# CmdInterpreter

# JarvisAPI
```python
JarvisAPI(self, jarvis)
```

Jarvis interface for plugins.

Plugins will receive a instance of this as the second (non-self) parameter
of the exec()-method.

Everything Jarvis-related that can't be implemented as a stateless-function
in the utilities-package should be implemented here.

## say
```python
JarvisAPI.say(self, text, color='')
```

This method give the jarvis the ability to print a text
and talk when sound is enable.
:param text: the text to print (or talk)
:param color: for text - use colorama (https://pypi.org/project/colorama/)
              e.g. Fore.BLUE

## input
```python
JarvisAPI.input(self, prompt='', color='')
```

Get user input

## input_number
```python
JarvisAPI.input_number(self, prompt='', color='', rtype=<class 'float'>, rmin=None, rmax=None)
```

Get user input: As number.

Guaranteed only returns number - ask user till correct number entered.

:param prompt: Printed to console
:param color: Color of prompot
:param rtype: type of return value; e.g. float (default) or int
:param rmin: Minum of values returned
:param rmax: Maximum of values returned

## connection_error
```python
JarvisAPI.connection_error(self)
```
Print generic connection error
## exit
```python
JarvisAPI.exit(self)
```
Immediately exit Jarvis
## notification
```python
JarvisAPI.notification(self, msg, time_seconds=0)
```

Sends notification msg in time_in milliseconds
:param msg: Message. Either String (message body) or tuple (headline, message body)
:param time_seconds: Time in seconds to wait before showing notification

## schedule
```python
JarvisAPI.schedule(self, time_seconds, function, *args)
```

Schedules function
After time_seconds call function with these parameter:
   - reference to this JarvisAPI instance
   - schedule_id (return value of this function)
   - *args
:return: integer, id - use with cancel

## cancel
```python
JarvisAPI.cancel(self, schedule_id)
```

Cancel event scheduled with schedule
:param schedule_id: id returned by schedule

## enable_voice
```python
JarvisAPI.enable_voice(self)
```

Use text to speech for every text passed to jarvis.say()

## disable_voice
```python
JarvisAPI.disable_voice(self)
```

Stop text to speech output for every text passed to jarvis.say()

## is_voice_enabled
```python
JarvisAPI.is_voice_enabled(self)
```

Returns True/False if voice is enabled/disabled with
enable_voice or disable_voice
Default: False (disabled)

## get_data
```python
JarvisAPI.get_data(self, key)
```

Get a specific key from memory

## add_data
```python
JarvisAPI.add_data(self, key, value)
```

Add a key and value to memory

## update_data
```python
JarvisAPI.update_data(self, key, value)
```

Updates a key with supplied value.

## del_data
```python
JarvisAPI.del_data(self, key)
```

Delete a key from memory

## eval
```python
JarvisAPI.eval(self, s)
```

Simulates typing 's' in Jarvis prompt

