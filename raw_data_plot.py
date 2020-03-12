import pyxdf
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import pywt
from feature_extraction_methods import waveform_length, mav, rms, stdev, entropy, frequencyMean, frequencyMedian, mmdf, mmnf, rawRMS, maxMag, absIntMag, absMeanMag
import numpy as np
from bisect import bisect

# time_series = data with two columns, [EMG0, EMG1]
 # time_stamps = timestamp
index = 1
time_series = []
time_stamps = []

Fs = 250

#fig1,axs1 = plt.subplots(2,2)

streams, fileheader = pyxdf.load_xdf('valve_03112020_trial14_openbci.xdf')

 # time_series = data with two columns, [EMG0, EMG1]
 # time_stamps = timestamp
index = 1
time_series = []
time_stamps = []
for ix,stream in enumerate(streams):
	#ix = 0 indicates the type of the streamline

	if(ix is 0):
		time_series0 = stream['time_series']
		time_stamps0 = stream['time_stamps']
		print("C")
		print(time_series0)
		print(time_stamps0)
		plt.plot(time_stamps0,time_series0)
	elif(ix is 1):
		time_series1 = stream['time_series']
		time_stamps1 = stream['time_stamps']
		print("D")
		print(time_series1)
		print(time_stamps1)
		#plt.plot(time_stamps1,time_series1)
	plt.show()
