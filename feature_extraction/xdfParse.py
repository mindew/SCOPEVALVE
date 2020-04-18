import pyxdf
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import pywt
from feature_extraction_methods import merge_event_lists,waveform_length, rms, stdev, entropy, frequencyMean, frequencyMedian, mmdf, mmnf, rawRMS, maxMag, absIntMag, absMeanMag
import numpy as np
from bisect import bisect
import csv

#OpenBCI sampling frequency is 250 Hz
Fs = 250

#Load data from the file
#INPUT THE NAME OF YOUR XDF FILE HERE:
streams, fileheader = pyxdf.load_xdf('valve_04162020_trial18_openbci.xdf')

# time_series = data with two columns, [EMG0, EMG1]
# time_stamps = timestamp
index = 1
time_series = []
time_stamps = []
#Load keyboard events and raw EMG data into state variables for feature extraction
for ix,stream in enumerate(streams):
	#ix = 0 indicates the type of the streamline
	#There is no way to ensure keyboard events or raw EMG always comes first, so we test to see 
	#whether the time_series is numerical or strings
	if(ix is 0):
		time_series0 = stream['time_series']
		time_stamps0 = stream['time_stamps']
		# figure out if stream is keyboard or femg
		if type(time_series0[0][0]) == str:
			keyboard_series = time_series0
			keyboard_timestamps = time_stamps0
		else:
			femg_series = np.array(time_series0)
			femg_timestamps = np.array(time_stamps0)

	elif(ix is 1):
		time_series1 = stream['time_series']
		time_stamps1 = stream['time_stamps']
		if type(time_series1[0][0]) == str:
			keyboard_series = time_series1
			keyboard_timestamps = time_stamps1
		else:
			femg_series = np.array(time_series1)
			femg_timestamps = np.array(time_stamps1)

	elif(ix is 2):
		time_series2 = stream['time_series']
		time_stamps2 = stream['time_stamps']

# pick out series and timestamps of when space, down, and left are pressed
space_series = []
space_timestamps = []
down_series = []
down_timestamps = []
rest_series = []
rest_timestamps = []
for i in range(0,len(keyboard_series)):
	if keyboard_series[i][0] == "SPACE pressed":
		space_series.append(keyboard_series[i][0])
		space_timestamps.append(keyboard_timestamps[i])
	elif keyboard_series[i][0] == 'DOWN pressed':
		down_series.append(keyboard_series[i][0])
		down_timestamps.append(keyboard_timestamps[i])
		rest_series.append(keyboard_series[i][0])
		rest_timestamps.append(keyboard_timestamps[i])
	#if the key press is not a space or down, but is a playtester keyboard event
	#add this to a third set of series/timestamps vectors
	elif keyboard_series[i][0] == 'LEFT pressed' or keyboard_series[i][0] == 'RIGHT pressed' or keyboard_series[i][0] == 'UP pressed':
		rest_series.append(keyboard_series[i][0])
		rest_timestamps.append(keyboard_timestamps[i])

# relative time of spacebar press to beginning of trial
# fEMG data and keyboard events are on different time scales,
# so we need to configure timestamps to be relative to the beginning of the test 
space_relstamps = []
for i in range(0,len(space_timestamps)):
	space_relstamps.append(space_timestamps[i]-femg_timestamps[0])

femg_relstamps = []
for i in range(0,len(femg_timestamps)):
	femg_relstamps.append(femg_timestamps[i]-femg_timestamps[0])

rest_relstamps = []
for i in range(0,len(rest_timestamps)):
	rest_relstamps.append(rest_timestamps[i]-femg_timestamps[0])

#noise reduction with a 5 Hz to 50 Hz bandpass and a 60 Hz notch filter
BandB,BandA = signal.butter(1,[5,50],'bandpass',fs=Fs,output='ba')
NotchB,NotchA = signal.iirnotch(60,1,fs=Fs)

# apply band pass and notch filters to both EMG data streams
EMG0 = signal.lfilter(BandB,BandA,femg_series[:,0])
EMG1 = signal.lfilter(BandB,BandA,femg_series[:,1])

EMG0 = signal.lfilter(NotchB,NotchA,EMG0)
EMG1 = signal.lfilter(NotchB,NotchA,EMG1)

# reduce noise associated with beginning of test by skipping first 16 seconds of meditation
EMG0,EMG1,femg_timestamps = EMG0[4000::],EMG1[4000::],femg_timestamps[4000::]

EMG0mirror = np.multiply(EMG0,-1)

inWindow = 0
currentListIndex = 0
space_feature0List = []
space_feature1List = []
space_timeList = []


#flagDone = 0
ind = 1
# in event identification, we only ever want a timestamp to be part of a 
# positive emotional event, negative emotional event, or non-emotional event
# so we track available timestamps, removing once a timestamp has been assigned
# to an event type
femg_relstamps_available = femg_relstamps
EMG0_available = EMG0
EMG1_available = EMG1

#first  we identify negative emotional events, which are indicated by space keyboard interference
while ind < len(space_relstamps)-1:
	nextInd = ind+1
	currInd = ind
	#check to see if the next space event happens within two seconds of the current space event
	while(space_relstamps[nextInd]<np.add(space_relstamps[currInd],2)):
		#if the next space event is within two seconds of the current, move to the next space event 
		currInd = nextInd
		nextInd = currInd+1
		#end this loop if we have reached the end of list of space events
		if(nextInd >= len(space_relstamps) or currInd >= len(space_relstamps)):
			break
	#If a two second event segment would exceed the length of the raw data vector, just go until
	#the end of the raw data vector
	if(space_relstamps[currInd]+2 > femg_relstamps[len(femg_relstamps)-1]):
		#find the starting and ending index of the event in the raw data vector
		startInd = bisect(femg_relstamps,space_relstamps[ind])
		endInd = len(femg_relstamps)-1
		#remove the new event segment from available unassigned data
		femg_relstamps_available = np.delete(femg_relstamps_available,range(startInd,endInd))
		EMG0_available = np.delete(EMG0,range(startInd-2500,endInd))
		EMG1_available = np.delete(EMG1,range(startInd-2500,endInd))
		#add the event segment to the list of positive emotional events
		space_timeList.append(femg_relstamps[startInd:endInd])
		space_feature0List.append(EMG0[startInd:endInd])
		space_feature1List.append(EMG1[startInd:endInd])
	else:
		#If there is only one space bar event between the beginning and end of this event
		#segment, then the event should be exactly two seconds long
		startInd = bisect(femg_relstamps,space_relstamps[ind])
		endInd = bisect(femg_relstamps,space_relstamps[currInd]+2)
		femg_relstamps_available = np.delete(femg_relstamps_available,range(startInd,endInd))
		EMG0_available = np.delete(EMG0,range(startInd-2500,endInd))
		EMG1_available = np.delete(EMG1,range(startInd-2500,endInd))
		space_timeList.append(femg_relstamps[startInd:endInd])
		space_feature0List.append(EMG0[startInd:endInd])
		space_feature1List.append(EMG1[startInd:endInd])
	ind = nextInd

down_timeList = []
down_feature0List = []
down_feature1List = []
ind = 0
#for positive emotional event identification, do the same thing as for negative emotional event
#identification, but also check to see if the prospective event segment is available still
while ind < len(rest_series)-1:
	flagNotThere = 0
	loopTriggered = 0
	#if there are a minimum of two consecutive down presses and the event segment space is available,
	#this should be a positive emotional event
	if(rest_series[ind] == 'DOWN pressed' and rest_series[ind+1] == 'DOWN pressed' and (femg_relstamps[bisect(femg_relstamps,rest_relstamps[ind])] in femg_relstamps_available)):
		startInd = bisect(femg_relstamps_available,rest_relstamps[ind])
		endInd = startInd
		ind += 1
		#continue extending the event segment until there are no more consecutive down presses
		while(ind<len(rest_series) and rest_series[ind] == 'DOWN pressed'):
			ind += 1
			#if the current down press timestamp is no longer available, close this event segment
			if(femg_relstamps[bisect(femg_relstamps,rest_relstamps[ind])] not in femg_relstamps_available):
				flagNotThere = 1
				break
			#otherwise continue
			else:
				endInd = bisect(femg_relstamps_available,rest_relstamps[ind])
				loopTriggered = 1
		#if the event segment would extend more than the length of the raw data vector, just go until
		#the end of the raw data vector
		if(endInd+500>len(femg_relstamps_available)):
			endInd = len(femg_relstamps)-1
		#otherwise the event segment should be two seconds longer than the last down press
		else:
			endInd += 500
		#at the end, add the event segment to the positive emotional event list and 
		#remove the event segment timestamps
		if((femg_relstamps_available[endInd]-femg_relstamps_available[endInd-500]) < 2.25 and not flagNotThere):
			down_timeList.append(femg_relstamps[startInd:endInd])
			down_feature0List.append(EMG0[startInd:endInd])
			down_feature1List.append(EMG1[startInd:endInd])
			femg_relstamps_available = np.delete(femg_relstamps_available,range(startInd,endInd))
			EMG0_available = np.delete(EMG0,range(startInd,endInd))
			EMG1_available = np.delete(EMG1,range(startInd,endInd))
	#if there are not two consecutive down presses, continue to iterate through the list
	else:
		ind += 1	

baseline_timeList = []
baseline_feature0List = []
baseline_feature1List = []
ind = 0
#break the remaining timestamps into two second baseline non-emotional event segments
while ind < len(femg_relstamps_available)-500:
	if(femg_relstamps_available[ind+500]-femg_relstamps_available[ind] > 2.008):
		ind += 1
	else:
		baseline_timeList.append(femg_relstamps_available[ind:ind+500])
		baseline_feature0List.append(EMG0[ind:ind+500])
		baseline_feature1List.append(EMG1[ind:ind+500])
		ind += 501

#merge the three different types of events into one merged event list in order of occurrence in testing
mergeEMG0,mergeEMG1,mergeTime,mergeEventType = merge_event_lists(space_feature0List,space_feature1List,space_timeList,down_feature0List,down_feature1List,down_timeList,baseline_feature0List,baseline_feature1List,baseline_timeList)

wavelet0List = []
wavelet1List = []

psd0List = []
psd1List = []

w = pywt.Wavelet('db4')

frequencyMean0List = []
frequencyMean1List = []
frequencyMedian0List = []
frequencyMedian1List = []
mmdf0List = []
mmdf1List = []
mmnf0List = []
mmnf1List = []
maxMag0List = []
maxMag1List = []
absMeanMag0List = []
absMeanMag1List = []
absIntMag0List = []
absIntMag1List = []
rawRMS0List = []
rawRMS1List = []
waveformLength0List = []
waveformLength1List = []
entropy0List = []
entropy1List = []
std0A6List = []
std0D6List = []
std0D5List = []
std0D4List = []
std0D3List = []
std0D2List = []
std0D1List = []
std1A6List = []
std1D6List = []
std1D5List = []
std1D4List = []
std1D3List = []
std1D2List = []
std1D1List = []

#for each of the events perform feature extraction
for (feature0,feature1) in zip(mergeEMG0,mergeEMG1):
	if(len(feature0) > 0 and len(feature1) > 0):
		#raw EMG feature extraction
		#maximum magnitude calculation
		#print(feature0)
		maxMag0List.append(maxMag(feature0))
		maxMag1List.append(maxMag(feature1))
		#mean of absolute value of raw emg
		absMeanMag0List.append(absMeanMag(feature0))
		absMeanMag1List.append(absMeanMag(feature1))
		#integral of absolute value of raw emg
		absIntMag0List.append(absIntMag(feature0))
		absIntMag1List.append(absIntMag(feature1))
		#RMS of raw EMG
		rawRMS0List.append(rawRMS(feature0))
		rawRMS1List.append(rawRMS(feature1))
		#Waveform length of raw EMG
		waveformLength0List.append(waveform_length(feature0))
		waveformLength1List.append(waveform_length(feature1))
		#wavelet generation
		c0A6,c0D6,c0D5,c0D4,c0D3,c0D2,c0D1 = pywt.wavedec(feature0, w, level=6)
		c1A6,c1D6,c1D5,c1D4,c1D3,c1D2,c1D1 = pywt.wavedec(feature1, w, level=6)
		#stdev
		std0A6,std0D6,std0D5,std0D4,std0D3,std0D2,std0D1 = stdev(c0A6),stdev(c0D6),stdev(c0D5),stdev(c0D4),stdev(c0D3),stdev(c0D2),stdev(c0D1)
		std1A6,std1D6,std1D5,std1D4,std1D3,std1D2,std1D1 = stdev(c1A6),stdev(c1D6),stdev(c1D5),stdev(c1D4),stdev(c1D3),stdev(c1D2),stdev(c1D1)
		std0A6List.append(std0A6)
		std0D6List.append(std0D6)
		std0D5List.append(std0D5)
		std0D4List.append(std0D4)
		std0D3List.append(std0D3)
		std0D2List.append(std0D2)
		std0D1List.append(std0D1)
		std1A6List.append(std1A6)
		std1D6List.append(std1D6)
		std1D5List.append(std1D5)
		std1D4List.append(std1D4)
		std1D3List.append(std1D3)
		std1D2List.append(std1D2)
		std1D1List.append(std1D1)
		#entropy - not using this but it's implemented
		entropy0List.append(entropy(wavelet0))
		entropy1List.append(entropy(wavelet1))
		#create a list of wavelets based on the list of events
		wavelet0List.append(wavelet0)
		wavelet1List.append(wavelet1)
		#PSD generation
		f0, Pxx0 = signal.welch(feature0, Fs)
		f1, Pxx1 = signal.welch(feature1, Fs)
		#frequency mean
		frequencyMean0List.append(frequencyMean(f0,Pxx0))
		frequencyMean1List.append(frequencyMean(f1,Pxx1))
		#frequency median
		frequencyMedian0List.append(frequencyMedian(Pxx0))
		frequencyMedian1List.append(frequencyMedian(Pxx1))
		#modified median frequency
		mmdf0List.append(mmdf(Pxx0))
		mmdf1List.append(mmdf(Pxx1))
		#modified mean frequency
		mmnf0List.append(mmnf(f0,Pxx0))
		mmnf1List.append(mmnf(f1,Pxx1))

#write CSV file with all of the feature extracted events
#there are two files, one for each facial EMG data stream
wtr0 = csv.writer(open('testSet0.csv','w'),delimiter = ',',lineterminator = '\n')
wtr0.writerow(maxMag0List)
wtr0.writerow(absMeanMag0List)
wtr0.writerow(absIntMag0List)
wtr0.writerow(rawRMS0List)
wtr0.writerow(waveformLength0List)
wtr0.writerow(frequencyMean0List)
wtr0.writerow(frequencyMedian0List)
wtr0.writerow(mmdf0List)
wtr0.writerow(mmnf0List)
wtr0.writerow(std0A6List)
wtr0.writerow(std0D6List)
wtr0.writerow(std0D5List)
wtr0.writerow(std0D4List)
wtr0.writerow(std0D3List)
wtr0.writerow(std0D2List)
wtr0.writerow(std0D1List)

wtr1 = csv.writer(open('testSet1.csv','w'),delimiter = ',',lineterminator = '\n')
wtr1.writerow(maxMag1List)
wtr1.writerow(absMeanMag1List)
wtr1.writerow(absIntMag1List)
wtr1.writerow(rawRMS1List)
wtr1.writerow(waveformLength1List)
wtr1.writerow(frequencyMean1List)
wtr1.writerow(frequencyMedian1List)
wtr1.writerow(mmdf1List)
wtr1.writerow(mmnf1List)
wtr1.writerow(std1A6List)
wtr1.writerow(std1D6List)
wtr1.writerow(std1D5List)
wtr1.writerow(std1D4List)
wtr1.writerow(std1D3List)
wtr1.writerow(std1D2List)
wtr1.writerow(std1D1List)

#a third csv file labels each event as either positive emotional (down)
#negative emotional (space) or baseline non-emotional (baseline)
with open("labelSet.csv","w") as csvWriter:
	writer = csv.writer(csvWriter)
	writer.writerow(mergeEventType)

fig, axs = plt.subplots(3,3)

axs[2,2].scatter(range(1,len(maxMag0List)),maxMag0List[1:],color="r")
axs[2,2].scatter(0,maxMag0List[0],color="b")
axs[2,2].set_title("Maximum Magnitude of EMG 0")

axs[2,1].scatter(range(1,len(maxMag1List)),maxMag1List[1:],color="r")
axs[2,1].scatter(0,maxMag1List[0],color="b")
axs[2,1].set_title("Maximum Magnitude of EMG 1")

axs[1,2].scatter(range(1,len(absMeanMag0List)),absMeanMag0List[1:],color="r")
axs[1,2].scatter(0,absMeanMag0List[0],color="b")
axs[1,2].set_title("Mean of Absolute Value of EMG 0")

axs[1,1].scatter(range(1,len(absMeanMag1List)),absMeanMag1List[1:],color="r")
axs[1,1].scatter(0,absMeanMag1List[0],color="b")
axs[1,1].set_title("Mean of Absolute Value of EMG 1")

axs[0,2].scatter(range(1,len(rawRMS0List)),rawRMS0List[1:],color="r")
axs[0,2].scatter(0,rawRMS0List[0],color="b")
axs[0,2].set_title("Root Mean Square of EMG 0")

axs[0,1].scatter(range(1,len(rawRMS1List)),rawRMS1List[1:],color="r")
axs[0,1].scatter(0,rawRMS1List[0],color="b")
axs[0,1].set_title("Root Mean Square of EMG 1")

axs[0,0].plot(femg_timestamps,EMG0)
axs[1,0].plot(femg_timestamps,EMG1)
axs[2,0].plot(femg_timestamps,EMG0)
axs[2,0].plot(femg_timestamps,EMG1)

#plt.show()
