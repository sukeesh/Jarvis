'''
NSSpeechSynthesizer driver.

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
from Foundation import *
from AppKit import NSSpeechSynthesizer
from PyObjCTools import AppHelper
from ..voice import Voice

def buildDriver(proxy):
    return NSSpeechDriver.alloc().initWithProxy(proxy)

class NSSpeechDriver(NSObject):
    def initWithProxy(self, proxy):
        self = super(NSSpeechDriver, self).init()
        if self:
            self._proxy = proxy
            self._tts = NSSpeechSynthesizer.alloc().initWithVoice_(None)
            self._tts.setDelegate_(self)
            # default rate
            self._tts.setRate_(200)
            self._completed = True
        return self

    def destroy(self):
        self._tts.setDelegate_(None)
        del self._tts

    def onPumpFirst_(self, timer):
        self._proxy.setBusy(False)

    def startLoop(self):
        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            0.0, self, 'onPumpFirst:', None, False)
        AppHelper.runConsoleEventLoop()

    def endLoop(self):
        AppHelper.stopEventLoop()

    def iterate(self):
        self._proxy.setBusy(False)
        yield

    def say(self, text):
        self._proxy.setBusy(True)
        self._completed = True
        self._proxy.notify('started-utterance')
        self._tts.startSpeakingString_(unicode(text))

    def stop(self):
        if self._proxy.isBusy():
            self._completed = False
        self._tts.stopSpeaking()

    def _toVoice(self, attr):
        return Voice(attr['VoiceIdentifier'], attr['VoiceName'],
                     [attr['VoiceLanguage']], attr['VoiceGender'],
                     attr['VoiceAge'])

    def getProperty(self, name):
        if name == 'voices':
            return [self._toVoice(NSSpeechSynthesizer.attributesForVoice_(v))
                     for v in list(NSSpeechSynthesizer.availableVoices())]
        elif name == 'voice':
            return self._tts.voice()
        elif name == 'rate':
            return self._tts.rate()
        elif name == 'volume':
            return self._tts.volume()
        else:
            raise KeyError('unknown property %s' % name)

    def setProperty(self, name, value):
        if name == 'voice':
            # vol/rate gets reset, so store and restore it
            vol = self._tts.volume()
            rate = self._tts.rate()
            self._tts.setVoice_(value)
            self._tts.setRate_(rate)
            self._tts.setVolume_(vol)
        elif name == 'rate':
            self._tts.setRate_(value)
        elif name == 'volume':
            self._tts.setVolume_(value)
        else:
            raise KeyError('unknown property %s' % name)

    def speechSynthesizer_didFinishSpeaking_(self, tts, success):
        if not self._completed:
            success = False
        else:
            success = True
        self._proxy.notify('finished-utterance', completed=success)
        self._proxy.setBusy(False)

    def speechSynthesizer_willSpeakWord_ofString_(self, tts, rng, text):
        self._proxy.notify('started-word', location=rng.location,
            length=rng.length)