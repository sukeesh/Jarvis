'''
Dummy driver that produces no output but gives all expected callbacks. Useful
for testing and as a model for real drivers.

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
from ..voice import Voice
import time

def buildDriver(proxy):
    '''
    Builds a new instance of a driver and returns it for use by the driver
    proxy.

    @param proxy: Proxy creating the driver
    @type proxy: L{driver.DriverProxy}
    '''
    return DummyDriver(proxy)

class DummyDriver(object):
    '''
    Dummy speech engine implementation. Documents the interface, notifications,
    properties, and sequencing responsibilities of a driver implementation.

    @ivar _proxy: Driver proxy that manages this instance
    @type _proxy: L{driver.DriverProxy}
    @ivar _config: Dummy configuration
    @type _config: dict
    @ivar _looping: True when in the dummy event loop, False when not
    @ivar _looping: bool
    '''
    def __init__(self, proxy):
        '''
        Constructs the driver.

        @param proxy: Proxy creating the driver
        @type proxy: L{driver.DriverProxy}
        '''
        self._proxy = proxy
        self._looping = False
        # hold config values as if we had a real tts implementation that
        # supported them
        voices = [
            Voice('dummy.voice1', 'John Doe', ['en-US', 'en-GB'], 'male', 'adult'),
            Voice('dummy.voice2', 'Jane Doe', ['en-US', 'en-GB'], 'female', 'adult'),
            Voice('dummy.voice3', 'Jimmy Doe', ['en-US', 'en-GB'], 'male', 10)
        ]
        self._config = {
            'rate' : 200,
            'volume' : 1.0,
            'voice' : voices[0],
            'voices' : voices
        }

    def destroy(self):
        '''
        Optional method that will be called when the driver proxy is being
        destroyed. Can cleanup any resources to make sure the engine terminates
        properly.
        '''
        pass

    def startLoop(self):
        '''
        Starts a blocking run loop in which driver callbacks are properly
        invoked.

        @precondition: There was no previous successful call to L{startLoop}
            without an intervening call to L{stopLoop}.
        '''
        first = True
        self._looping = True
        while self._looping:
            if first:
                self._proxy.setBusy(False)
                first = False
            time.sleep(0.5)

    def endLoop(self):
        '''
        Stops a previously started run loop.

        @precondition: A previous call to L{startLoop} suceeded and there was
            no intervening call to L{endLoop}.
        '''
        self._looping = False

    def iterate(self):
        '''
        Iterates from within an external run loop.
        '''
        self._proxy.setBusy(False)
        yield

    def say(self, text):
        '''
        Speaks the given text. Generates the following notifications during
        output:

        started-utterance: When speech output has started
        started-word: When a word is about to be spoken. Includes the character
            "location" of the start of the word in the original utterance text
            and the "length" of the word in characters.
        finished-utterance: When speech output has finished. Includes a flag
            indicating if the entire utterance was "completed" or not.

        The proxy automatically adds any "name" associated with the utterance
        to the notifications on behalf of the driver.

        When starting to output an utterance, the driver must inform its proxy
        that it is busy by invoking L{driver.DriverProxy.setBusy} with a flag
        of True. When the utterance completes or is interrupted, the driver
        inform the proxy that it is no longer busy by invoking
        L{driver.DriverProxy.setBusy} with a flag of False.

        @param text: Unicode text to speak
        @type text: unicode
        '''
        self._proxy.setBusy(True)
        self._proxy.notify('started-utterance')
        i = 0
        for word in text.split(' '):
            self._proxy.notify('started-word', location=i, length=len(word))
            try:
                i = text.index(' ', i+1)+1
            except Exception:
                pass
        self._proxy.notify('finished-utterance', completed=True)
        self._proxy.setBusy(False)

    def stop(self):
        '''
        Stops any current output. If an utterance was being spoken, the driver
        is still responsible for sending the closing finished-utterance
        notification documented above and resetting the busy state of the
        proxy.
        '''
        pass

    def getProperty(self, name):
        '''
        Gets a property value of the speech engine. The suppoted properties
        and their values are:

        voices: List of L{voice.Voice} objects supported by the driver
        voice: String ID of the current voice
        rate: Integer speech rate in words per minute
        volume: Floating point volume of speech in the range [0.0, 1.0]

        @param name: Property name
        @type name: str
        @raise KeyError: When the property name is unknown
        '''
        try:
            return self._config[name]
        except KeyError:
            raise KeyError('unknown property %s' % name)

    def setProperty(self, name, value):
        '''
        Sets one of the supported property values of the speech engine listed
        above. If a value is invalid, attempts to clip it / coerce so it is
        valid before giving up and firing an exception.

        @param name: Property name
        @type name: str
        @param value: Property value
        @type value: object
        @raise KeyError: When the property name is unknown
        @raise ValueError: When the value cannot be coerced to fit the property
        '''
        if name == 'voice':
            v = filter(lambda v: v.id == value, self._config['voices'])
            self._config['voice'] = v[0]
        elif name == 'rate':
            self._config['rate'] = value
        elif name == 'volume':
            self._config['volume'] = value
        else:
            raise KeyError('unknown property %s' % name)