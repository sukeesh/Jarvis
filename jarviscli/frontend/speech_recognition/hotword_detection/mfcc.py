"""This module is used for calculating the MFCC feature vectors for the input speech utterance. The following sequence of steps are followed:

1. Pre-emphasizing input utterance by passing it through a first order HPF
2. Dividing utterance into non-overlapping frames
3. Computing DFT of each frame
4. Passing each frame through the Mel filterbank and calculating the energy passed by each filter
5. Computing logarithm of filterbank energies
6. Computing DCT of log filterbank energies and extracting first 13 coefficients
7. Appending spectral dynamic features to give a 39 dimensional feature vector for each frame"""
import time
import timeit

import numpy as np
from scipy.fftpack import dct


class MFCC:
    """
    This class contains all methods and parameters related to MFCC calculation.

    :param alpha: Parameter used in pre-emphasis filtering. Should lie between 0 and 1
    :type alpha: float
    :param N: Number of points used for computing DFT
    :type N: int
    :param fs: Sampling frequency
    :type fs: int
    :param frame_dur: Duration of 1 frame in seconds
    :type frame_due: float

    Documentation related to all methods of this class is described below.

    """

    def __init__(self, alpha=0.95, N=256, fs=8000, eps=10e-6, frame_dur=0.025):
        self.alpha = alpha  # Preemphasis parameter
        self.N = N	     # No of FFT points
        self.eps = eps       # eps to avoid mathematical errors
        self.fs = fs
        self.mfcc_frame_length = round(fs*frame_dur)  # frame length for mfcc
        self.prev_frame = np.zeros((14,))
        self.prev_prev_frame = np.zeros((14,))

    def generate_filter_bank(self, num_filters=23, lower_freq=300, upper_freq=3800):
        """
        This function computes the Mel filterbank. The filters are stored in rows, the columns correspond
        to DFT bins. The filters are returned as a matrix of size nfilt * (nfft/2 + 1)

        :param num_filters: Number of filters in the Mel filterbank
        :type num_filters: int
        :param lower_freq: Lower frequency from where the first filter should start
        :type lower_freq: int
        :param upper_freq: Upper frequency where the last filter should end. Should be less than (fs/2)
        :type upper_freq: int
        :returns: Matrix containing filterbank weights
        :rtype: matrix

        """
        self.highfreq = upper_freq
        assert self.highfreq <= self.fs/2, "highfreq is greater than samplerate/2"

        # compute points evenly spaced in mels
        self.lowmel = self.hz2mel(lower_freq)
        self.highmel = self.hz2mel(upper_freq)
        self.melpoints = np.linspace(self.lowmel, self.highmel, num_filters+2)
        self.bin = np.floor((self.N+1)*self.mel2hz(self.melpoints)/self.fs)

        self.fbank = np.zeros([num_filters, int(self.N/2)+1])
        for j in range(0, num_filters):
            for i in range(int(self.bin[j]), int(self.bin[j+1])):
                self.fbank[j, i] = (i - self.bin[j]) / (self.bin[j+1]-self.bin[j])
            for i in range(int(self.bin[j+1]), int(self.bin[j+2])):
                self.fbank[j, i] = (self.bin[j+2]-i) / (self.bin[j+2]-self.bin[j+1])
        return self.fbank

    def hz2mel(self, hz):
        """
        Function for converting frequency in Hertz to Mel scale
        """
        return 2595 * np.log10(1+hz/700.0)

    def mel2hz(self, mel):
        """
        Function for converting frequency in Mel scale to Hertz		
        """
        return 700*(10**(mel/2595.0)-1)

    def compute_mfcc(self, input_frame, include_dc=False):
        """
        This function performs all the steps as mentioned earlier inorder to calculate 39 dimensional MFCC feature vector for an input frame.

        :param input_frame: Frame of audio from which MFCC features have to be extracted
        :type input_frame: array
        :param include_dc: Used to indicate whether or not the 1st MFCC coefficient is to be included
        :type include_dc: boolean
        :returns: 39 dimensional MFCC vector
        :rtype: array
        """
        self.windowed_frame = input_frame * np.hamming(len(input_frame))  # Hamming Windowing input frame
        self.pre_frame = self.windowed_frame - self.alpha * \
            np.concatenate((np.full(1, 0), self.windowed_frame[:-1]))  # Preemphasis
        self.fft_frame = np.fft.rfft(self.pre_frame, self.N)  # Computing FFT
        self.mel_fb_sq_weights = self.generate_filter_bank()**2
        self.mel_frame = np.log(np.dot(self.mel_fb_sq_weights, (np.abs(self.fft_frame)**2)) +
                                self.eps)  # Passing through mel and taking log
        self.mel_frame_normalized = self.mel_frame / \
            np.sum(self.mel_fb_sq_weights, axis=1)  # normalizing by filter energies
        self.dct_frame = dct(self.mel_frame_normalized)  # Computing DCT
        self.delta = self.dct_frame[0:14] - self.prev_frame
        self.double_delta = self.dct_frame[0:14] - self.prev_prev_frame
        self.coeffs = np.append(self.dct_frame[0:14], [self.delta[1:14], self.double_delta[1:14]])
        self.prev_prev_frame = self.prev_frame
        self.prev_frame = self.dct_frame[0:14]
        if (include_dc):
            return self.coeffs  	# Returning 39 MFCC coefficients
        else:
            return self.coeffs[1:40]
