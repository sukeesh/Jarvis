"""This module is used for computing the DTW distance between two utterances."""
import math

import numpy as np


def euclideanDistance(a, b):
    """

    This function computes the simple Euclidean distance between two MFCC vectors. This is further useful in DTW distance computation.

    :param a: MFCC vector 1
    :type a: array
    :param b: MFCC vector 2
    :type b: array
    :returns: Euclidean distance between MFCC vectors 1 and 2
    :rtype: float

    """
    return np.sqrt(np.abs(np.sum(np.dot(a, a) - np.dot(b, b))))


class DTW:
    """

    This class contains methods and parameters used for computing the DTW distance between training and test utterances. 

    Documentation related to all methods in this class is described below.

    """

    def __init__(self, distFunc=euclideanDistance):
        self.distFunc = distFunc

    def compute_distance(self, reference, test):
        """
        This function computes the DTW distance between two utterances by constructing a distance matrix.

        :param reference: Matrix containing MFCC vectors of training utterance
        :type reference: matrix
        :param test: Matrix containing MFCC vectors of test utterance
        :param test: matrix
        :returns: DTW distance between reference and test utterance
        :rtype: float

        """
        if (type(reference) is str):
            reference = list(reference)
        if (type(test) is str):
            test = list(test)
        if (type(reference) is list):
            reference = np.array(reference)
        if (type(test) is list):
            test = np.array(test)
        DTW_matrix = np.empty([reference.shape[0], test.shape[0]])
        DTW_matrix[:] = np.inf

        DTW_matrix[0, 0] = 0

        for i in range(reference.shape[0]):
            for j in range(test.shape[0]):
                cost = euclideanDistance(reference[i, :], test[j, :])
                r_index = i-1
                c_index = j-1
                if(r_index < 0):
                    r_index = 0
                if(c_index < 0):
                    c_index = 0
                DTW_matrix[i, j] = cost + min(DTW_matrix[r_index, j], DTW_matrix[i,
                                                                                 c_index], DTW_matrix[r_index, c_index])
        return DTW_matrix[-1, -1]/(test.shape[0]+reference.shape[0])
