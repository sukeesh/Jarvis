"""This module is used for recording speech utterances both for training as well as testing purposes. PyAudio is required for this module."""
import sys
import wave
from array import array
from struct import pack

import pyaudio


class wordRecorder:
    """

    This class contains methods for recording audio from a microphone, segmenting audio to remove noise by using an amplitude based VAD and for storing segmented utterances in an appropriate folder.

    :param samplingFrequency: Frequency at which we want to sample audio
    :type samplingFrequency: int
    :param threshold: Threshold used for amplitude based VAD (scaled in the range 0-16384)
    :type threshold: int

    Documentation related to all member functions is listed below.

    """

    def __init__(self, samplingFrequency=8000, threshold=14000):
        self.samplingFrequency = samplingFrequency
        self.threshold = threshold

    def isSilent(self, data):
        """

        This function is used to check if the whole recorded audio is silence or not. If it is silence, then this utterance is discarded.

        :param data: Recorded audio 
        :type data: array
        :returns: 1 if entire audio is silence and 0 otherwise
        :rtype: boolean

        """
        return max(data) < self.threshold

    def normalize(self, data):
        """

        This function is used to normalize the sampled audio stream such that all values lie in the range -16383 to 16384. This is because we use a 16-bit representation to store audio. Out of these 16 bits 1 bit is reserved as a sign bit.

        :param data: Recorded audio
        :type data: array
        :returns: Normalized audio
        :rtype: array

        """
        maxShort = 16384
        scale = float(maxShort)/max(abs(i) for i in data)

        r = array('h')
        for i in data:
            r.append(int(i*scale))
        return r

    def trimWord(self, data):
        """

        This function implements the amplitude based Voice Activity detector. It segments out audio based on whether the amplitude of the audio is greater than the specified threshold or not.

        :param data: Normalized audio
        :type data: array
        :returns: Trimmed audio containing only speech segments
        :rtype: array

        """
        def trimStart(data):
            snd_started = False
            r = array('h')

            for i in data:
                if not snd_started and abs(i) > self.threshold:
                    snd_started = True
                    r.append(i)

                elif snd_started:
                    r.append(i)
            return r

        data = trimStart(data)
        data.reverse()
        data = trimStart(data)
        data.reverse()
        return data

    def record(self):
        """

        This function implements the recording routine used for getting audio from a microphone using PyAudio. It also calls the ``normalize()`` and ``trimWord()`` methods to return the normalized and trimmed audio containing speech only.

        :returns: Trimmed and normalized recorded audio
        :rtype: array

        """
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=self.samplingFrequency,
                        input=True, output=False, frames_per_buffer=1024)

        num_silent = 0
        snd_started = False

        r = array('h')

        for i in range(int(self.samplingFrequency*2/1024)):
            snd_data = array('h', stream.read(1024))
            r.extend(snd_data)

        sample_width = p.get_sample_size(pyaudio.paInt16)
        stream.stop_stream()
        stream.close()
        p.terminate()

        r = self.normalize(r)
        r = self.trimWord(r)
        return sample_width, r

    def record2File(self, path):
        """

        This function is used to store the recorded audio after it has been normalized and trimmed into a specified directory as a .wav file.

        :param path: Path to directory where audio is to be stored
        :type data: str

        """
        sample_width, data = self.record()
        data = pack('<' + ('h'*len(data)), *data)

        wf = wave.open(path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(sample_width)
        wf.setframerate(self.samplingFrequency)
        wf.writeframes(data)
        wf.close()
