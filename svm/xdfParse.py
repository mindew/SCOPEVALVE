import pyxdf
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import pywt

Fs = 250

import numpy as np

def window_rms(a, window_size):
  a2 = np.power(a,2)
  window = np.ones(window_size)/float(window_size)
  return np.sqrt(np.convolve(a2, window, 'valid'))

def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

streams, fileheader = pyxdf.load_xdf('minju_training_02202020.xdf')
 #retrieve time_series and time_stamps
index = 1
time_series = []
time_stamps = []
for ix,stream in enumerate(streams):
	#print(ix)
	#print(stream)
	if(ix is 0):
		time_series0 = stream['time_series']
		time_stamps0 = stream['time_stamps']
		#Uncomment the below lines if you want to convert ms to seconds or minutes
		#time_columns = np.true_divide(time_stamps0,3600)
		#for time_stamp in time_stamps0:
		#	plt.axvline(x=time_stamp,linewidth=.5)
		#plt.plot(time_stamps0,time_series0[:,0])
	elif(ix is 1):
		time_series1 = stream['time_series']
		time_stamps1 = stream['time_stamps']
		#time_points = np.true_divide(time_stamps1,3600)
		#plt.plot(time_stamps1,time_series1[:,0])
		#plt.plot(time_stamps1,time_series1[:,1])
	elif(ix is 2):
		time_series2 = stream['time_series']
		time_stamps2 = stream['time_stamps']

BandB,BandA = signal.butter(4,30,'low',fs=Fs,output='ba')
EMG0 = signal.lfilter(BandB,BandA,time_series0[:,0])
EMG1 = signal.lfilter(BandB,BandA,time_series0[:,1])
EMG0baseline = EMG0[0:14999]
EMG0 = EMG0[100::]
EMG1baseline = EMG1[0:14999]
EMG1 = EMG1[100::]
baselineAVG0 = np.mean(EMG0)
baselineSTD0 = np.std(EMG0)
baselineAVG1 = np.mean(EMG1)
baselineSTD1 = np.std(EMG1)
threshold0 = baselineAVG0 - 1.5*baselineSTD0
threshold1 = baselineAVG1 - 1.5*baselineSTD1
threshold2 = baselineAVG0 + 1.5*baselineSTD0
threshold3 = baselineAVG1 + 1.5*baselineSTD1
#0 - 1.5 minutes breating
#2 - 3 frowning
#3 - 4 smiling
#4 - 4:30 frowning 3 times
"""
averageEMG1 = np.mean(EMG1)
EMG1sub = np.subtract(EMG1,averageEMG1)
EMG1square = np.square(EMG1sub)
EMG1avg = moving_average(EMG1square,10)
rmsEMG1 = np.sqrt(EMG1avg)
"""
rmsEMG1 = window_rms(EMG1,20)


inWindow = 0
currentListIndex = 0
featureList = []
"""
for i in range(0,len(EMG1)):
	if(inWindow and np.abs(EMG1[i]) > threshold):
		featureList[currentListIndex].append(EMG1[i])
	elif(inWindow and not np.abs(EMG1[i]) > threshold):
		currentListIndex = currentListIndex + 1
		inWindow = 0
	elif(not inWindow and np.abs(EMG1[i]) > threshold):
		featureList[currentListIndex] = [EMG1[i]]
"""
waveletList = []

#apply window
for feature in featureList:
	blackman = signal.windows.blackman(len(feature))
	feature = np.multiply(feature,blackman)
	wavelet = pywt.dwt(feature,'db4')
	waveletList.append(wavelet)

#plt.plot(rmsEMG1)
for time,event in zip(time_stamps2,time_series2):
	"""if(event[0] is 'UP pressed'):
		print(HI)
		plt.axvline(x=time,color='r')
	elif(event[0] is 'RIGHT pressed'):
		print(HI)
		plt.axvline(x=time,color='b')
	elif(event[0] is 'LEFT pressed'):
		print(HI)
		plt.axvline(x=time,color='g')
	elif(event[0] is 'SPACE pressed'):
		print(HI)
		plt.axvline(x=time,color='c')"""
	plt.axvline(x=time,color='b')
#plt.hlines(threshold0,0,len(EMG0))
#plt.hlines(threshold1,0,len(EMG1))
#plt.hlines(threshold2,0,len(EMG0))
#plt.hlines(threshold3,0,len(EMG1))

plt.plot(time_stamps0,EMG0)
plt.plot(time_stamps0,EMG1)
plt.show()
