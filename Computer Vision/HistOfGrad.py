import os
import sys
from skimage.io import imread
from skimage.transform import resize
from skimage.feature import hog
from skimage.color import rgb2gray
import matplotlib.pyplot as plt
from skimage.segmentation import chan_vese
from matplotlib import cm
import numpy as np
import pandas as pd
import random

def makeHoG():
    H = 120#240#480
    W = 160#320#640

    cwd = os.getcwd()

    X_train = None
    Y_train = None

    trainingFiles = getListOfPics()
    x=0
    for pic in trainingFiles:
        # Read image
        try:
            img = imread(pic) 
        except:
            continue
        

        # resize image to size of camera 640x480
        resized_img = resize(img, (H, W))

        imgray = rgb2gray(resized_img)

        cv = chan_vese(imgray, mu=0.25, lambda1=1, lambda2=1, tol=1e-3,
               max_num_iter=200, dt=0.5, init_level_set="checkerboard",
               extended_output=True)
        #plt.imsave(cwd+"\\Computer Vision\\seg\\segtest-HOG.png",cv[0])

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
        elif ("OK" in pic):
            label = "OK"
            y= 2
        else:
            label = "Not-Hand"
            y=1

        splitPic = pic.split("\\")
        splitPic = splitPic[len(splitPic)-1].split(".")
        #plt.imsave(cwd+"\\Computer Vision\\HoG\\"+splitPic[0]+"-HOG.png",hog_image, cmap = cm.gray)

        
        # Add to X training array
        if(X_train is None):
            X_train = fd
        else:
            X_train = np.vstack([X_train, fd])

        #   Add to Y training the label based off of name
        if(Y_train is None):
            Y_train = y
        else:
            Y_train = np.vstack([Y_train, y])
        x=x+1

        if(x%100==0):
            print(str(x)+"/"+str(len(trainingFiles)))
    print("Done")
    # save the dataframe as a csv file
    DF = pd.DataFrame(X_train)
    DF.to_csv(cwd+"\\Computer Vision\\CSVs\\X_trainingData7-CabPeople.csv")
 
    # save the dataframe as a csv file
    DFy = pd.DataFrame(Y_train)
    DFy.to_csv(cwd+"\\Computer Vision\\CSVs\\Y_trainingData7-CabPeople.csv")
    


def getListOfPics():
    #get list of all images
    cwd = os.getcwd()

    handsPath = cwd +"\\Computer Vision\\Inputs\\Hands"
    handsFiles = os.listdir(handsPath)
    handsFiles = [cwd+"\\Computer Vision\\Inputs\\Hands\\" +x for x in handsFiles if random.randint(0, 5)==2]

    WoodPath = cwd +"\\Computer Vision\\Inputs\\House"
    WoodFiles = os.listdir(WoodPath)
    WoodFiles = [cwd+"\\Computer Vision\\Inputs\\House\\" +x for x in WoodFiles]

    moreHandPath = cwd +"\\Computer Vision\\Inputs\\meHand"
    moreHandFiles = os.listdir(moreHandPath)
    moreHandFiles = [cwd+"\\Computer Vision\\Inputs\\meHand\\" +x for x in moreHandFiles]

    okHandPath = cwd +"\\Computer Vision\\Inputs\\OK"
    okHandFiles = os.listdir(okHandPath)
    okHandFiles = [cwd+"\\Computer Vision\\Inputs\\OK\\" +x for x in okHandFiles]

    trainingFiles =    handsFiles + WoodFiles  + moreHandFiles #+ okHandFiles

    return trainingFiles

	

makeHoG()

