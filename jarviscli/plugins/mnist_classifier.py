import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import torch, torchvision
from torch import nn

from plugin import plugin

#Fully connected NN with one hidden layer
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

@plugin("Clssify MNIST type image")
def mnist_classifier(jarvis, s):

    try:
    
        #Path of the image.
        imgPath = s

        #Load the image.
        try:
            img = cv.imread(imgPath)
        except:
            jarvis.say("Something went wrong during the loading of the image.")


        #Check if the shape of the image is right(28x28)
        if( not((np.shape(img)[0] == 28) and (np.shape(img)[1] == 28)) ):
            jarvis.say("The image you gave me isn't Mnist type image.")
            return

        #Check if the image is black and white
        isBlackAndWhite = True
        for row in range(28):
            for col in range(28):
                if( not(img[row][col][0] == pix[row][col][1] and pix[row][col][1] == pix[row][col][2]) ):
                    isBlackAndWhite = False
                    break

        if(isBlackAndWhite == False):
            jarvis.say("The image you gave me isn't Mnist type image.")
            return

             
        #Show the image.
        plt.rcParams['toolbar'] = 'None'
        plt.figure(num=imgPath)
        plt.imshow(img)
        plt.show()

        #Take the information we need from the pixels
        #(The mnist type images are black and white so we only need one channel of the RGB channels)
        data = []
        for row in range(28):
            for col in range(28):
                pix = img[row][col][0]
                data.append(pix)
        data = np.asarray(data, dtype=np.float32)
        data = torch.from_numpy(np.multiply(1.0/255, data))

        
        #Load my pre-trained mnist classifier model
        try:
            myModel = torch.load("MyMnistModel.pth")
            myModel.eval()
        except:
            jarvis.say("Something went wrong during the loading of my inteligence.")

        #Predict the representation of the image
        with torch.no_grad():
            data = data.reshape(-1, 28*28)
            outputs = myModel(data)
            _, predicted = torch.max(outputs.data,1)
            jarvis.say("According to my knowledge the image you gave me represents the digit {}.".format(predicted.item()))

    except:
        jarvis.say("Something went wrong. Try again.")
