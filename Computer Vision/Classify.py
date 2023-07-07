import numpy as np
from sklearn import svm
import cv2
import skops.io as sio

from skimage.transform import resize
from skimage.feature import hog

Hmodel =   240#480 120
Wmodel =  320#640 160

Hmodel =   120
Wmodel =   160

Him = 480
Wim = 640

def ClassifyImage(clf, img):
    #load model
    #clf = sio.load("Computer Vision\\models\\model1-plainSVM.skops", trusted=True)

    #img = imread(image)
    resized_img = resize(img, (Hmodel, Wmodel))
    fd, hog_image = hog(resized_img, 
                    orientations=9, 
                    pixels_per_cell=(8, 8),
                    cells_per_block=(2, 2), 
                    visualize=True, 
                    channel_axis = -1)
    (x,) = fd.shape
    fd = np.reshape(fd, (1, x))
    guess = clf.predict(fd)
    #probs = clf.predict_proba(fd)
    probs = -1
    print(guess)
    return (guess, probs)

def SlidingWindow(clf, image):
    (Wim, Him, rbgs) = image.shape
    WinSizes = [(Wim, Him), (Wim/2, Him/2)]#, (Wim/4, Him/4)], (Wim/8, Him/8)]
    for (WinH, WinW) in WinSizes:
        WinH = int(WinH)
        WinW = int(WinW)
        for x in range(0, Wim, int(WinW/2)):
            for y in range(0, Him,int(WinH/2)):
                img = image[x:x+WinW,y:y+WinH]
                resized_img = resize(img, (Hmodel, Wmodel))
                fd, hog_image = hog(resized_img, 
                                orientations=9, 
                                pixels_per_cell=(8, 8),
                                cells_per_block=(2, 2), 
                                visualize=True, 
                                channel_axis = -1)
                cv2.imshow("currwindow", resized_img)
                cv2.waitKey(500)
                (f,) = fd.shape
                fd = np.reshape(fd, (1, f))
                guess = clf.predict(fd)
                
                print(guess)
                if((y+WinH)>=Him):
                    break
            if((x+WinW)>=Wim):
                break