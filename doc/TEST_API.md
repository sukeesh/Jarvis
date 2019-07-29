# tests

# PluginTest
```python
PluginTest(self, methodName='runTest')
```

## load_plugin
```python
PluginTest.load_plugin(self, plugin_class)
```

Returns Plugin Instance (object).
Works for both callable classes or methods.

Adds method run(string) - which execute plugin using mocked api.

## queue_input
```python
PluginTest.queue_input(self, msg)
```

Queue msg to be returned by 'jarvis.input()'

## histroy_call
```python
PluginTest.histroy_call(self)
```

Returns MockHistory instance. Fields:

1. operation (string)
2. args (tuple)
3. return value

## history_say
```python
PluginTest.history_say(self)
```

Returns MockHistory instance. Fields:

1. text (string)
2. color (colorama.Fore.*)

## history_notification
```python
PluginTest.history_notification(self)
```

Returns MockHistory instance. Fields:

1. msg (string)
2. time_seconds (int)

## history_schedule
```python
PluginTest.history_schedule(self)
```

Returns MockHistory instance. Fields:

1. time_seconds (int)
2. function
3. args (tuple)

# MockHistory
```python
MockHistory(self)
```

Record/Output history.

Recorded data sets must contain fixed and predefined number of "fields" (e.g. text and color).

Note: For Methods with first parameter "field" method "name_field" exist.
So "view('text')" can be rewritten as "view_text".

## record
```python
MockHistory.record(self, *args)
```

Do not call manually!

## contains
```python
MockHistory.contains(self, field=None, value=None)
```

Check if value is recorded.
If field is None, value should be a tuple of values
for all fields.

## view
```python
MockHistory.view(self, field=None, index=None)
```

Returns value.

If field is None, returns tuple of all values for all fields.
If index is None, returns all recorded values

## last
```python
MockHistory.last(self, field=None)
```
Shortcut for view with index -1
## get_length
```python
MockHistory.get_length(self)
```
Returns how many data sets were recorded
