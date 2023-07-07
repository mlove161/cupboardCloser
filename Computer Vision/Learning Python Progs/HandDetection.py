#importing required libraries
from skimage.io import imread
from skimage import color
from skimage.transform import resize
from skimage.feature import hog
from skimage import exposure
import matplotlib.pyplot as plt
import os
import sys
from matplotlib import cm
import numpy as np
from sklearn import svm
import winsound
import cv2

H = 640
W = 480

#get list of all images
cwd = os.getcwd()
handsPath = cwd +"\\Computer Vision\\Hands"
WoodPath = cwd +"\\Computer Vision\\wood"

handsFiles = os.listdir(handsPath)
handsFiles = [cwd+"\\Computer Vision\\Hands\\" +x for x in handsFiles]
WoodFiles = os.listdir(WoodPath)
WoodFiles = [cwd+"\\Computer Vision\\wood\\" +x for x in WoodFiles]
print("got all file names")
img = imread(WoodFiles[0])

trainingFiles =  handsFiles + WoodFiles

def get_HOG(start, end, Files, X_train, Y_train):
    x=start
    #Loop through images
    for pic in Files:
        # Read image
        img = imread(pic)

        # resize image to size of camera 640x480
        resized_img = resize(img, (H, W))

        #   hog image 
        fd, hog_image = hog(resized_img, 
                        orientations=9, 
                        pixels_per_cell=(8, 8),
                	    cells_per_block=(2, 2), 
                        visualize=True, 
                        channel_axis = -1)

        #   grayscale hog
        if("Hand" in pic):
            label = "Hand"
            y= 0
        else:
            label = "Wood"
            y=1

        plt.imsave(cwd+"\\Computer Vision\\HoG\\"+str(x)+"-"+label+"-HOG.png",hog_image, cmap = cm.gray)
        x= x+1



        # reshape to be a 1D array
        image = np.reshape(hog_image, (H*W, 1))

        # Add to X training array
        if(X_train is None):
            X_train = image
        else:
            X_train = np.hstack([X_train, image])

        #   Add to Y training the label based off of name
        if(Y_train is None):
            Y_train = y
        else:
            Y_train = np.hstack([Y_train, y])



        if(x==end):
            break
    return (X_train, Y_train)


def createTraining():
    print("cool")
    X_train = None
    Y_train = None 
    for pic in HogFiles:
        img = imread(pic, cv2.IMREAD_GRAYSCALE)

        # reshape to be a 1D array
        image = color.rgb2gray(img)
        image = np.reshape(img, (H*W, 1))
        

        # Add to X training array
        if(X_train == None):
            X_train = image
        else:
            X_train = np.hstack(X_train, image)

        #   Add to Y training the label based off of name
        if("Hand" in pic):
            y = 0
        else:
            y = 1

        if(Y_train == None):
            Y_train = y
        else:
            Y_train = np.hstack(Y_train, y)

    return X_train, Y_train

#make svm classifier
#train it to classifier

#test classifier
X_train = None
Y_train = None 
print("getting pics")
(X_train, Y_train) = get_HOG(0,4, handsFiles, X_train, Y_train)
print("done with hand pics")
(X_train, Y_train) = get_HOG(4,8, WoodFiles, X_train, Y_train)
print("done with else")

HOGPath = cwd +"\\Computer Vision\\HoG"
HogFiles = os.listdir(HOGPath)
HogFiles = [cwd+"\\Computer Vision\\HoG\\" +x for x in HogFiles]
createTraining()


clf = svm.SVC()
(x,) = Y_train.shape
Y_train = np.reshape(Y_train, (x, ))

(x1,y1) = X_train.shape
X_train = np.reshape(X_train, (y1, x1))

clf.fit(X_train, Y_train)

def testit (clf, picname):
    img = imread(picname)
    resized_img = resize(img, (H, W))
    fd, hog_image = hog(resized_img, 
                    orientations=9, 
                    pixels_per_cell=(8, 8),
                    cells_per_block=(2, 2), 
                    visualize=True, 
                    channel_axis = -1)
    image = np.reshape(hog_image, (1, H*W))

    guess = clf.predict(image)
    print(guess)

testit(clf, 'image_testing/hand-1.jpg')
testit(clf, 'image_testing/hand-2.jpg')
testit(clf, 'image_testing/Hand_0000058.jpg')
testit(clf, 'image_testing/Face.jpg')
testit(clf, 'image_testing/Book.jpg')
testit(clf, 'image_testing/ceiling.jpg')

winsound.Beep(2500, 2000)