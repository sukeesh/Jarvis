import cv2 as cv
#import matplotlib.pyplot as plt
import numpy as np
import torch
import torchvision
from torch import nn

from plugin import plugin

# Fully connected NN with one hidden layer


class myNN(nn.Module):
    def __init__(self, input_size=784, num_classes=10):
        super(myNN, self).__init__()
        self.fullyCon1 = nn.Linear(input_size, 256)
        self.relu1 = nn.ReLU()
        self.fullyCon2 = nn.Linear(256, num_classes)

    def forward(self, x):
        out = self.fullyCon1(x)
        out = self.relu1(out)
        out = self.fullyCon2(out)
        return out


@plugin("classify")
def mnist_classifier(jarvis, s):
    """
    This script takes the path of an image, reshapes the image to 28x28 if it isn't,
    checks if it is black and white and then tells what digit this image represents,
    according to our pre-trained neural network model that we have loaded.  
    """

    # Path of the image.
    imgPath = s

    # Load the image.
    try:
        img = cv.imread(imgPath)
    except:
        jarvis.say("Something went wrong during the loading of the image.")
        return

    # Check if the shape of the image is right(28x28)
    if(not((np.shape(img)[0] == 28) and (np.shape(img)[1] == 28))):
        jarvis.say("The shape of the image you gave me isn't right. I will reshape it to 28x28.")
        img = cv.resize(img, (28, 28), interpolation = cv.INTER_AREA)

    # Check if the image is in the shades of black and white
    def is_black_and_white(pixel):
        return pixel[0] == pixel[1] and pixel[1] == pixel[2]

    isBlackAndWhite = True
    for row in range(28):
        for col in range(28):
            if(not(is_black_and_white(img[col][row]))):
                isBlackAndWhite = False
                break

    if(isBlackAndWhite == False):
        jarvis.say("The image you gave me isn't black and white.")
        return

    # Show the image.
    #plt.rcParams['toolbar'] = 'None'
    #plt.figure(num=imgPath)
    #plt.imshow(img)
    #plt.show()

    # Take the information we need from the pixels
    # (The mnist type images are black and white so we only need one channel of the RGB channels)
    data = []
    for row in range(28):
        for col in range(28):
            pix = img[row][col][0]
            data.append(pix)
    data = np.asarray(data, dtype=np.float32)
    data = torch.from_numpy(np.multiply(1.0/255, data))

    # Load my pre-trained mnist classifier model
    myModel = torch.load("jarviscli/data/MyMnistModel.pth")
    myModel.eval()

    # Predict the representation of the image
    with torch.no_grad():
        data = data.reshape(-1, 28*28)
        outputs = myModel(data)
        _, predicted = torch.max(outputs.data, 1)
        jarvis.say("According to my knowledge the image you gave me represents the digit {}.".format(predicted.item()))
