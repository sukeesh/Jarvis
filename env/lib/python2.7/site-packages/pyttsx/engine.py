'''
Speech engine front-end.

Copyright (c) 2009, 2013 Peter Parente

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
'''
import driver
import traceback
import weakref

class Engine(object):
    '''
    @ivar proxy: Proxy to a driver implementation
    @type proxy: L{DriverProxy}
    @ivar _connects: Array of subscriptions
    @type _connects: list
    @ivar _inLoop: Running an event loop or not
    @type _inLoop: bool
    @ivar _driverLoop: Using a driver event loop or not
    @type _driverLoop: bool
    @ivar _debug: Print exceptions or not
    @type _debug: bool
    '''
    def __init__(self, driverName=None, debug=False):
        '''
        Constructs a new TTS engine instance.

        @param driverName: Name of the platform specific driver to use. If
            None, selects the default driver for the operating system.
        @type: str
        @param debug: Debugging output enabled or not
        @type debug: bool
        '''
        self.proxy = driver.DriverProxy(weakref.proxy(self), driverName, debug)
        # initialize other vars
        self._connects = {}
        self._inLoop = False
        self._driverLoop = True
        self._debug = debug

    def _notify(self, topic, **kwargs):
        '''
        Invokes callbacks for an event topic.

        @param topic: String event name
        @type topic: str
        @param kwargs: Values associated with the event
        @type kwargs: dict
        '''
        for cb in self._connects.get(topic, []):
            try:
                cb(**kwargs)
            except Exception, e:
                if self._debug: traceback.print_exc()

    def connect(self, topic, cb):
        '''
        Registers a callback for an event topic. Valid topics and their
        associated values:

        started-utterance: name=<str>
        started-word: name=<str>, location=<int>, length=<int>
        finished-utterance: name=<str>, completed=<bool>
        error: name=<str>, exception=<exception>

        @param topic: Event topic name
        @type topic: str
        @param cb: Callback function
        @type cb: callable
        @return: Token to use to unregister
        @rtype: dict
        '''
        arr = self._connects.setdefault(topic, [])
        arr.append(cb)
        return {'topic' : topic, 'cb' : cb}

    def disconnect(self, token):
        '''
        Unregisters a callback for an event topic.

        @param token: Token of the callback to unregister
        @type token: dict
        '''
        topic = token['topic']
        try:
            arr = self._connects[topic]
        except KeyError:
            return
        arr.remove(token['cb'])
        if len(arr) == 0:
            del self._connects[topic]

    def say(self, text, name=None):
        '''
        Adds an utterance to speak to the event queue.

        @param text: Text to sepak
        @type text: unicode
        @param name: Name to associate with this utterance. Included in
            notifications about this utterance.
        @type name: str
        '''
        self.proxy.say(text, name)

    def stop(self):
        '''
        Stops the current utterance and clears the event queue.
        '''
        self.proxy.stop()

    def isBusy(self):
        '''
        @return: True if an utterance is currently being spoken, false if not
        @rtype: bool
        '''
        return self.proxy.isBusy()

    def getProperty(self, name):
        '''
        Gets the current value of a property. Valid names and values include:

        voices: List of L{voice.Voice} objects supported by the driver
        voice: String ID of the current voice
        rate: Integer speech rate in words per minute
        volume: Floating point volume of speech in the range [0.0, 1.0]

        Numeric values outside the valid range supported by the driver are
        clipped.

        @param name: Name of the property to fetch
        @type name: str
        @return: Value associated with the property
        @rtype: object
        @raise KeyError: When the property name is unknown
        '''
        return self.proxy.getProperty(name)

    def setProperty(self, name, value):
        '''
        Adds a property value to set to the event queue. Valid names and values
        include:

        voice: String ID of the voice
        rate: Integer speech rate in words per minute
        volume: Floating point volume of speech in the range [0.0, 1.0]

        Numeric values outside the valid range supported by the driver are
        clipped.

        @param name: Name of the property to fetch
        @type name: str
        @param: Value to set for the property
        @rtype: object
        @raise KeyError: When the property name is unknown
        '''
        self.proxy.setProperty(name, value)

    def runAndWait(self):
        '''
        Runs an event loop until all commands queued up until this method call
        complete. Blocks during the event loop and returns when the queue is
        cleared.

        @raise RuntimeError: When the loop is already running
        '''
        if self._inLoop:
            raise RuntimeError('run loop already started')
        self._inLoop = True
        self._driverLoop = True
        self.proxy.runAndWait()

    def startLoop(self, useDriverLoop=True):
        '''
        Starts an event loop to process queued commands and callbacks.

        @param useDriverLoop: If True, uses the run loop provided by the driver
            (the default). If False, assumes the caller will enter its own
            run loop which will pump any events for the TTS engine properly.
        @type useDriverLoop: bool
        @raise RuntimeError: When the loop is already running
        '''
        if self._inLoop:
            raise RuntimeError('run loop already started')
        self._inLoop = True
        self._driverLoop = useDriverLoop
        self.proxy.startLoop(self._driverLoop)

    def endLoop(self):
        '''
        Stops a running event loop.

        @raise RuntimeError: When the loop is not running
        '''
        if not self._inLoop:
            raise RuntimeError('run loop not started')
        self.proxy.endLoop(self._driverLoop)
        self._inLoop = False

    def iterate(self):
        '''
        Must be called regularly when using an external event loop.
        '''
        if not self._inLoop:
            raise RuntimeError('run loop not started')
        elif self._driverLoop:
            raise RuntimeError('iterate not valid in driver run loop')
        self.proxy.iterate()