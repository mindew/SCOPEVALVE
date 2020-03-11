import pyxdf
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import pywt
from feature_extraction_methods import waveform_length, mav, rms, stdev, entropy, frequencyMean, frequencyMedian, mmdf, mmnf
import numpy as np

# sampling frequency is 250, default number set by Cyton Board
Fs = 250

streams, fileheader = pyxdf.load_xdf('valve_02262020_trial5_openbci.xdf')
 #retrieve time_series and time_stamps

 # time_series = data with two columns, [EMG0, EMG1]
 # time_stamps = timestamp
index = 1
time_series = []
time_stamps = []
data_info = []

for ix,stream in enumerate(streams):
	#ix = 0 indicates the type of the streamline
	if(ix is 0):
		time_series0 = stream['time_series']
		time_stamps0 = stream['time_stamps']
		data_info0 = stream['info']
		print(data_info0[data_info0.keys()[0]])
		print("next")
		#Uncomment the below lines if you want to convert ms to seconds or minutes
		#time_columns = np.true_divide(time_stamps0,3600)
		#for time_stamp in time_stamps0:
		#	plt.axvline(x=time_stamp,linewidth=.5)
		#plt.plot(time_stamps0,time_series0[:,0])
	elif(ix is 1):
		time_series1 = stream['time_series']
		time_stamps1 = stream['time_stamps']
		data_info1 = stream['info']
		print(data_info1)
		print("next")
		# print(streams['info'])
		#time_points = np.true_divide(time_stamps1,3600)
		#plt.plot(time_stamps1,time_series1[:,0])
		#plt.plot(time_stamps1,time_series1[:,1])
	elif(ix is 2):
		time_series2 = stream['time_series']
		time_stamps2 = stream['time_stamps']
		data_info2 = stream['info']
		print(data_info2)
		#print(stream['info'])

