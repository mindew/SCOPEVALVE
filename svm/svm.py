import pandas as pd
from scipy import signal
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
import pywt
from pyOpenBCI import OpenBCICyton
import numpy as np

categories = ['Pasta','Pies','Salads']

dataset = []
numDataPoints = 5000
def store_data(sample):
	dataset.append(sample.channels_data)
	if(len(dataset) is numDataPoints):
		filterAndClassify(dataset)

board = OpenBCICyton(port='/dev/ttyUSB*')

def trainClassifier():
	data = pd.read_csv("multi_classifier.csv")
	training_set, test_set = train_test_split(data, test_size = 0.2, random_state = 1)
	X_train = training_set.iloc[:,0:4].values
	X_test = test_set.iloc[:,0:4].values

	i = 0
	for category in categories:
		classifiers[i] = SVC(kernel='linear', random_state = 1, probability=True)
		classifiers[i].fit(X_train,training_set[category])
		Y_pred = classifiers[i].predict(X_test)
		pred = classifiers[i].predict_log_proba(X_test)
		print(category)
		print(Y_pred)
		print(pred)
		print('Test accuracy is {}'.format(accuracy_score(test_set[category],Y_pred)))

	return classifiers

def filterAndClassify(dataset):
	#format dataset
	fEMG0 = dataset[:,1]
	fEMG1 = dataset[:,3]
	#Perform the wavelet transform on both datasets
	wavelet0 = pywt.dwt(fEMG0,'db4')
	wavelet1 = pywt.dwt(fEMG1,'db4')
	#filter EMG data
	Fs = 250 #Hz
	BandB,BandA = signal.butter(4,[30,500],'hp',fs=Fs,output='ba')
	NotchB,NotchA = signal.iirnotch(50,10,Fs)
	#apply filter to fEMG0
	bandPass0 = signal.lfilter(BandB,BandA,wavelet0)
	notched0 = signal.lfilter(NotchB,NotchA,bandPass0)
	#apply filter to fEMG1
	bandPass1 = signal.lfilter(BandB,BandA,wavelet1)
	notched1 = signal.lfilter(NotchB,NotchA,bandPass1)
	#apply moving average filter to both datasetss
	convolveFilter = np.ones((1,31))/31
	filtered0 = np.convolve(notched0,convolveFilter,mode='full')
	filtered1 = np.convolve(notched1,convolveFilter,mode='full')

	classifiers = trainClassifier()

	testData = [filtered0, filtered1]

	for num in range(0,len(categories)):
		outPrediction[:,num] = classifiers[num].predict(testData)


# take a window based on button press
# automatic game interference every 5th or 20th move
# Andrew Ng Coursera Class
# Fei Fei Li 
# Data science
# temporal features in addition to power features
# Convolution

# EMG Project with Neurotech class
# Do we need help getting things over the finish line


