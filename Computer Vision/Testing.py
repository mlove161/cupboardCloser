import cv2
from Classify import ClassifyImage
from Classify import SlidingWindow
import skops.io as sio
from skimage.io import imread
import os
import random
from skimage.transform import resize
from skimage.feature import hog
import numpy as np

def TestClassifier():
    clf = sio.load("Computer Vision\\models\\model7-NN-CabPeople.skops", trusted=True)
    
   
    
    print("Try Sliding Win")
    #img = imread("Computer Vision\\image_testing/Hand/slidingT.jpg")
    #SlidingWindow(clf, img)
    
    print("done with sliding")
    cwd = os.getcwd()

    handsPath = cwd +"\\Computer Vision\\Inputs\\Hands"
    handsFiles = os.listdir(handsPath)
    handsFiles = [cwd+"\\Computer Vision\\Inputs\\Hands\\" +x for x in handsFiles if random.randint(0, 21)==2]

    handsPath = cwd +"\\Computer Vision\\image_testing\\Hand"
    handsFiles2 = os.listdir(handsPath)
    handsFiles2 = [cwd+"\\Computer Vision\\image_testing\\Hand\\" +x for x in handsFiles2]

    handsPath = cwd +"\\Computer Vision\\image_testing\\Not"
    nothandsFiles = os.listdir(handsPath)
    nothandsFiles = [cwd+"\\Computer Vision\\image_testing\\Not\\" +x for x in nothandsFiles]

    AllF = handsFiles2 + nothandsFiles #+ handsFiles 

    X_test = None
    Y_test = None

    correct = 0
    total = 0
    wrongList = []
    for t in AllF:
        img = imread(t)
        (guess, probs) = ClassifyImage(clf, img)

        if("Hand" in t):
            y= 0
        else:
            y=1

        if(int(guess[0]) == y):
            correct = correct+1
        else:
            wrongList.append(t)
        total = total + 1

    print(str(correct)+" / "+ str(total))
    print(str(correct/total))
    print(wrongList)
    
def TestCameraClassification():
    clf = sio.load("Computer Vision\\models\\model2-NN-accCamGood.skops", trusted=True)

    cap = cv2.VideoCapture(1)

    while True:
        ok, img = cap.read()

        if not ok:
            print("oh no!")
            continue
        ClassifyImage(clf, img)
        cv2.imshow("camera test", img)
        cv2.waitKey(500)

#TestCameraClassification()
TestClassifier()