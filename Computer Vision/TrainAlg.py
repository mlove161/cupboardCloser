import numpy as np
from sklearn import svm
from sklearn.neural_network import MLPClassifier
import skops.io as sio
import os

def TrainAlg():
    #get data
    (X_train, Y_train) = GetData()

    clf = MLPClassifier(solver='lbfgs', alpha=1e-3,hidden_layer_sizes=(15, 5), random_state=1) #, max_iter=10000000000
    #svm.SVC(kernel='rbf', degree=3)
    Y_train= Y_train[:,1:]
    (x,y) = Y_train.shape 
    Y_train = np.reshape(Y_train, (x, ))

    X_train= X_train[:,1:]
    (x1,y1) = X_train.shape  #X_train = np.reshape(X_train, (y1, x1))

    #train alg
    clf.fit(X_train, Y_train)

    cwd = os.getcwd()
    #save model
    obj = sio.dump(clf, cwd+"\\Computer Vision\\models\\model7-NN-CabPeople.skops")

def GetData():
    cwd = os.getcwd()
    X_train = np.loadtxt(cwd+"\\Computer Vision\\CSVs\\X_trainingData7-CabPeople.csv",
                 delimiter=",", dtype=str)
    Y_train = np.loadtxt(cwd+"\\Computer Vision\\CSVs\\Y_trainingData7-CabPeople.csv",
                 delimiter=",", dtype=str)
    return (X_train, Y_train)


TrainAlg()