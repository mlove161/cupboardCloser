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


# clf name: location to the classifier to load, should be a file in AWS I guess?
# img: array of pixels that represents an image (hopefully feeding in the pixel array should work) 
def ClassifyImage(clfName, img):
    #load model
    clf = sio.load(clfName, trusted=True)

    #read image (if given an image file)
    #img = imread(image)

    # pre proccessing
    resized_img = resize(img, (Hmodel, Wmodel))
    fd, hog_image = hog(resized_img, 
                    orientations=9, 
                    pixels_per_cell=(8, 8),
                    cells_per_block=(2, 2), 
                    visualize=True, 
                    channel_axis = -1)
    (x,) = fd.shape
    fd = np.reshape(fd, (1, x))

    #predict if hand or not
    guess = clf.predict(fd) # if this fails it is probably bc HW of model is wrong

    #get probability (never figured out how to do it out)
    #probs = clf.predict_proba(fd)

    print(guess)
    return guess