"""This module detects the trained hotword using the mfcc,dtw and wordrecorder classes. The following sequence of steps are followed:

1. Compute MFCC feature vectors of the test utterance
2. Compute DTW distance between the test utterance and each of the 10 stored training utterances using these MFCC vectors
3. Compute the mean of these DTW distances
4. If the mean of these distances is greater than some threshold then no hotword is present otherwise hotword is present"""
import os

import dtw
import mfcc
import numpy as np
import scipy.io.wavfile as wv


class hwDetector:
    """

    This class contains methods which accomplish the end goal of hotword detection using methods defined in mfcc,dtw and wordrecorder classes.

    :param samplingFrequency: Sampling frequency of audio
    :type samplingFrequency: int
    :param framePeriod: Duration of 1 frame in seconds
    :type framePeriod: float
    :param hopPeriod: Frame hopping duration in seconds
    :type hopPeriod: float
    :param trainDir: Path to directory containing training utterances
    :type trainDir: str
    :param thresh: Threshold used for DTW distance 
    :type thresh: float

    Documentation related to all methods in this class is described below.

    """

    def __init__(self, samplingFrequency=8000, framePeriod=25e-3, hopPeriod=10e-3, trainDir="./train_audio/", thresh=6):
        self.samplingFrequency = samplingFrequency
        self.framePeriod = framePeriod
        self.hopPeriod = hopPeriod
        self.trainDir = trainDir
        self.thresh = thresh
        self.hopLength = int(samplingFrequency * hopPeriod)
        self.frameLength = int(samplingFrequency * framePeriod)
        self.referenceMFCC = []
        for file_name in os.listdir(trainDir):
            if file_name.endswith(".wav"):
                (fs, data) = wv.read(trainDir + file_name)
                num_frames = int(data.shape[0]/self.hopLength) - int(np.ceil(self.frameLength/self.hopLength))
                if num_frames <= 0:
                    continue
                print('OK')

                MFCC_calculator = mfcc.MFCC()
                MFCC_MATRIX = np.empty([39, num_frames])
                for k in range(num_frames):
                    MFCC_MATRIX[:, k] = MFCC_calculator.compute_mfcc(
                        data[k*self.hopLength: k*self.hopLength + self.frameLength])
                self.referenceMFCC.append(MFCC_MATRIX)

        DTW_calculator = dtw.DTW()
        distance_list = [DTW_calculator.compute_distance(np.transpose(matrix), np.transpose(
            matrix2)) for matrix in self.referenceMFCC for matrix2 in self.referenceMFCC]
        self.thresh = np.mean(np.array((distance_list)))*1.2

    def distance(self, fileName):
        """

        This function is used for calculating the DTW distance between the test utterance and each of the 10 training utterances.

        :param fileName: Name of test utterance .wav file
        :type fileName: str
        :returns: List of DTW distances of test utterance with each training utterance
        :rtype: list

        """
        DTW_calculator = dtw.DTW()
        (fs, data) = wv.read(fileName)
        num_frames = int(data.shape[0]/self.hopLength) - int(np.ceil(self.frameLength/self.hopLength))
        if num_frames <= 0:
            return 10000

        MFCC_calculator = mfcc.MFCC()
        MFCC_MATRIX = np.empty([39, num_frames])
        for k in range(num_frames):
            MFCC_MATRIX[:, k] = MFCC_calculator.compute_mfcc(
                data[k*self.hopLength: k*self.hopLength + self.frameLength])

        distance_list = [DTW_calculator.compute_distance(np.transpose(
            matrix), np.transpose(MFCC_MATRIX)) for matrix in self.referenceMFCC]
        return distance_list

    def isHotword(self, fileName):
        """

        This function computes the mean of the calculated DTW distances and returns a True value if mean distance is less than a specified threshold. If mean distance is greater than threshold it returns False indicating absence of hotword.

        :param fileName: Name of test utterance .wav file
        :type fileName: str
        :returns: True/False to indicate presence/absence of hotword
        :rtype: Boolean

        """
        distances = np.array(self.distance(fileName))
        mean_dist = np.mean(distances)
        if (mean_dist < self.thresh):
            return True
        return False
