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

fig1,axs1 = plt.subplots(2,2)

streams, fileheader = pyxdf.load_xdf('valve_03042020_trial10_openbci.xdf')

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
        # figure out if stream is keyboard or femg
		if type(time_series0[0][0]) == str:
			keyboard_series = time_series0
			keyboard_timestamps = time_stamps0
		else:
			femg_series = time_series0
			femg_timestamps = time_stamps0
		axs1[0,0].plot(time_stamps0,time_series0)
		BandB,BandA = signal.butter(1,[5,50],'bandpass',fs=Fs,output='ba')
		NotchB,NotchA = signal.iirnotch(60,1,fs=Fs)
		EMG0 = signal.lfilter(BandB,BandA,time_series0[:,0])
		EMG1 = signal.lfilter(BandB,BandA,time_series0[:,1])
		EMG0 = signal.lfilter(NotchB,NotchA,EMG0)
		EMG1 = signal.lfilter(NotchB,NotchA,EMG1)

		axs1[1,0].plot(time_stamps0,EMG0)
		axs1[1,0].plot(time_stamps0,EMG1)
		#Uncomment the below lines if you want to convert ms to seconds or minutes
		#time_columns = np.true_divide(time_stamps0,3600)
		#for time_stamp in time_stamps0:
		#	plt.axvline(x=time_stamp,linewidth=.5)
		#plt.plot(time_stamps0,time_series0[:,0])
	elif(ix is 1):
		time_series1 = stream['time_series']
		time_stamps1 = stream['time_stamps']
        # figure out if stream is keyboard or femg
		if type(time_series1[0][0]) == str:
			keyboard_series = time_series1
			keyboard_timestamps = time_stamps1
		else:
			femg_series = time_series1
			femg_timestamps = time_stamps1
		#time_points = np.true_divide(time_stamps1,3600)
		#plt.plot(time_stamps1,time_series1[:,0])
		#plt.plot(time_stamps1,time_series1[:,1])
	# elif(ix is 2):
	# 	time_series2 = stream['time_series']
	# 	time_stamps2 = stream['time_stamps']"""

# pick out series and timestamps of when space is pressed
space_series = []
space_timestamps = []
for i in range(0,len(keyboard_series)):
	if keyboard_series[i][0] == "SPACE pressed":
		space_series.append(keyboard_series[i][0])
		space_timestamps.append(keyboard_timestamps[i])

# relative time of spacebar press to beginning of trial
space_relstamps = []
for i in range(0,len(space_timestamps)):
	space_relstamps.append(space_timestamps[i]-femg_timestamps[0])

print(space_timestamps)

#.1, 30
BandB,BandA = signal.butter(1,[5,50],'bandpass',fs=Fs,output='ba')
NotchB,NotchA = signal.iirnotch(60,1,fs=Fs)
 # return butterworth digital filter coeff(1st order, [critical frequency], passtype, 
 # sampling frequency, output type - numerator / denominator)

 # apply low pass filter (one dimension only)
 # acquired numerator coeff, denominator coeff, array
EMG0 = signal.lfilter(BandB,BandA,time_series0[:,0])
EMG1 = signal.lfilter(BandB,BandA,time_series0[:,1])

EMG0 = signal.lfilter(NotchB,NotchA,EMG0)
EMG1 = signal.lfilter(NotchB,NotchA,EMG1)

axs1[1,0].plot(time_stamps0,EMG0)
axs1[1,0].plot(time_stamps0,EMG1)
# EMG0 = Zygomaticus --> frowning
# EMG1 = 

# parsing each column to 1by1 vector
EMG0,EMG1,time_stamps0 = EMG0[4000::],EMG1[4000::],time_stamps0[4000::]

EMG0mirror = np.multiply(EMG0,-1)

axs1[0,1].plot(time_stamps0,EMG0)
axs1[0,1].plot(time_stamps0,EMG1)

axs1[1,1].plot(time_stamps0,EMG0mirror)
axs1[1,1].plot(time_stamps0,EMG1)


inWindow = 0
currentListIndex = 0
feature0List = []
feature1List = []
timeList = []

feature0List.append(EMG0[7500:7999])
feature1List.append(EMG1[7500:7999])
timeList.append(time_stamps0[7500:7999])

"""for i in range(0,len(EMG1)):
	if(inWindow and ((EMG0[i] < threshold0 or EMG0[i] > threshold2) or (EMG1[i] < threshold1 or EMG1[i] > threshold3))):
		feature0List[currentListIndex].append(EMG0[i])
		feature1List[currentListIndex].append(EMG1[i])
		timeList[currentListIndex].append(time_stamps0[i])
	elif(inWindow and not (EMG0[i] < threshold0 or EMG0[i] > threshold2) and not (EMG1[i] < threshold1 or EMG1[i] > threshold3)):
		currentListIndex = currentListIndex + 1
		inWindow = 0
	elif(not inWindow and((EMG0[i] < threshold0 or EMG0[i] > threshold2) or (EMG1[i] < threshold1 or EMG1[i] > threshold3))):
		feature0List.append([])
		feature1List.append([])
		timeList.append([])
		timeList[currentListIndex].append(time_stamps0[i])
		feature0List[currentListIndex].append(EMG0[i])
		feature1List[currentListIndex].append(EMG1[i])
		inWindow = 1"""

flagDone = 0
ind = 0

while ind < len(space_timestamps)-1:
	nextInd = ind+1
	currInd = ind
	if(nextInd >= len(space_timestamps) or currInd >= len(space_timestamps)):
		break
	while(space_timestamps[nextInd]<np.add(space_timestamps[currInd],2)):
		currInd = nextInd
		nextInd = currInd+1
		if(nextInd >= len(space_timestamps) or currInd >= len(space_timestamps)):
			flagDone = 1
			break
	if(flagDone and (space_timestamps[currInd]+2 <= time_stamps0[len(time_stamps0)-1])):
		startInd = bisect(time_stamps0,space_timestamps[ind])
		endInd = bisect(time_stamps0,space_timestamps[ind])+499
		timeList.append(time_stamps0[startInd:endInd])
		feature0List.append(EMG0[startInd:endInd])
		feature1List.append(EMG1[startInd:endInd])
		flagDone = 0
	elif(flagDone):
		startInd = bisect(time_stamps0,space_timestamps[ind])
		timeList.append(time_stamps0[startInd:])
		feature0List.append(EMG0[startInd:])
		feature1List.append(EMG1[startInd:])
		flagDone = 0
	else:
		if(ind is currInd):
			startInd = bisect(time_stamps0,space_timestamps[ind])
			endInd = startInd + 499
		else: 
			startInd = bisect(time_stamps0,space_timestamps[ind])
			endInd = bisect(time_stamps0,space_timestamps[currInd])
		print("START IND:")
		print(space_timestamps[ind])
		timeList.append(time_stamps0[startInd:endInd])
		feature0List.append(EMG0[startInd:endInd])
		feature1List.append(EMG1[startInd:endInd])
	ind = nextInd

#print(feature0List)

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


#apply window
for (feature0,feature1) in zip(feature0List,feature1List):
	#raw EMG feature extraction
	#maximum magnitude calculation
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
	#wavelet generation
	blackman = signal.windows.blackman(len(feature0))
	feature0 = [a*b for a,b in zip(feature0,blackman)]
	feature1 = [a*b for a,b in zip(feature1,blackman)]
	wavelet0 = pywt.wavedec(feature0, w, level=6)
	wavelet1 = pywt.wavedec(feature1, w, level=6)
	wavelet0List.append(wavelet0)
	wavelet1List.append(wavelet1)
	#PSD generation
	f0, Pxx0 = signal.welch(feature0, Fs)
	f1, Pxx1 = signal.welch(feature1, Fs)
	frequencyMean0List.append(frequencyMean(f0,Pxx0))
	frequencyMean1List.append(frequencyMean(f1,Pxx1))
	frequencyMedian0List.append(frequencyMedian(Pxx0))
	frequencyMedian1List.append(frequencyMedian(Pxx1))
	mmdf0List.append(mmdf(Pxx0))
	mmdf1List.append(mmdf(Pxx1))
	mmnf0List.append(mmnf(f0,Pxx0))
	mmnf1List.append(mmnf(f1,Pxx1))
	

length0List = []
length1List = []
mav0List = []
mav1List = []
rms0List = []
rms1List = []
stdev0List = []
stdev1List = []
entropy0List = []
entropy1List = []

for (wavelet0, wavelet1) in zip(wavelet0List,wavelet1List):
	#waveform length 
	c0A6,c0D6,c0D5,c0D4,c0D3,c0D2,c0D1 = wavelet0
	c1A6,c1D6,c1D5,c1D4,c1D3,c1D2,c1D1 = wavelet1
	length0A6,length0D6,length0D5,length0D4,length0D3,length0D2,length0D1 = waveform_length(c0A6),waveform_length(c0D6),waveform_length(c0D5),waveform_length(c0D4),waveform_length(c0D3),waveform_length(c0D2),waveform_length(c0D1)
	length1A6,length1D6,length1D5,length1D4,length1D3,length1D2,length1D1 = waveform_length(c1A6),waveform_length(c1D6),waveform_length(c1D5),waveform_length(c1D4),waveform_length(c1D3),waveform_length(c1D2),waveform_length(c1D1)
	length0List.append([length0A6,length0D6,length0D5,length0D4,length0D3,length0D2,length0D1])
	length1List.append([length1A6,length1D6,length1D5,length1D4,length1D3,length1D2,length1D1])
	#mav 
	mav0A6,mav0D6,mav0D5,mav0D4,mav0D3,mav0D2,mav0D1 = mav(c0A6),mav(c0D6),mav(c0D5),mav(c0D4),mav(c0D3),mav(c0D2),mav(c0D1)
	mav1A6,mav1D6,mav1D5,mav1D4,mav1D3,mav1D2,mav1D1 = mav(c1A6),mav(c1D6),mav(c1D5),mav(c1D4),mav(c1D3),mav(c1D2),mav(c1D1)
	mav0List.append([mav0A6,mav0D6,mav0D5,mav0D4,mav0D3,mav0D2,mav0D1])
	mav1List.append([mav1A6,mav1D6,mav1D5,mav1D4,mav1D3,mav1D2,mav1D1])
	#rms
	rms0A6,rms0D6,rms0D5,rms0D4,rms0D3,rms0D2,rms0D1 = rms(c0A6),rms(c0D6),rms(c0D5),rms(c0D4),rms(c0D3),rms(c0D2),rms(c0D1)
	rms1A6,rms1D6,rms1D5,rms1D4,rms1D3,rms1D2,rms1D1 = rms(c1A6),rms(c1D6),rms(c1D5),rms(c1D4),rms(c1D3),rms(c1D2),rms(c1D1)
	rms0List.append([rms0A6,rms0D6,rms0D5,rms0D4,rms0D3,rms0D2,rms0D1])
	rms1List.append([rms1A6,rms1D6,rms1D5,rms1D4,rms1D3,rms1D2,rms1D1])
	#stdev
	std0A6,std0D6,std0D5,std0D4,std0D3,std0D2,std0D1 = stdev(c0A6),stdev(c0D6),stdev(c0D5),stdev(c0D4),stdev(c0D3),stdev(c0D2),stdev(c0D1)
	std1A6,std1D6,std1D5,std1D4,std1D3,std1D2,std1D1 = stdev(c1A6),stdev(c1D6),stdev(c1D5),stdev(c1D4),stdev(c1D3),stdev(c1D2),stdev(c1D1)
	stdev0List.append([std0A6,std0D6,std0D5,std0D4,std0D3,std0D2,std0D1])
	stdev1List.append([std1A6,std1D6,std1D5,std1D4,std1D3,std1D2,std1D1])
	#entropy
	entropy0List.append(entropy(wavelet0))
	entropy1List.append(entropy(wavelet1))

#feature extraction
#wavelet = waveletList[0]
i = 0
#while i < (len(wavelet)-1):


fig, axs = plt.subplots(3,3)

"""zeroA6List = [event[0] for event in length0List]
zeroD6List = [event[1] for event in length0List]
zeroD5List = [event[2] for event in length0List]
zeroD4List = [event[3] for event in length0List]
zeroD3List = [event[4] for event in length0List]
zeroD2List = [event[5] for event in length0List]
zeroD1List = [event[6] for event in length0List]

oneA6List = [event[0] for event in length1List]
oneD6List = [event[1] for event in length1List]
oneD5List = [event[2] for event in length1List]
oneD4List = [event[3] for event in length1List]
oneD3List = [event[4] for event in length1List]
oneD2List = [event[5] for event in length1List]
oneD1List = [event[6] for event in length1List]"""

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

"""axs[1,2].scatter(range(len(oneD4List[:-1])),zeroD4List[:-1],color="r")
axs[2,0].scatter(range(len(oneD4List[:-1])),oneD4List[:-1],color="b")
axs[2,0].scatter(len(oneD4List),oneD4List[len(oneD4List)-1],color="g")

#plt.plot(rmsEMG1)
for time in space_timestamps:
	axs[0,0].axvline(x=time,color='b')
	axs[0,0].set_title("Raw EMG 0 Data")
	axs[1,0].axvline(x=time,color='b')
	axs[1,0].set_title("Raw EMG 1 Data")
	axs[2,0].axvline(x=time,color='b')
	axs[2,0].set_title("Raw EMG 0 and 1 Data")
if(event[0] is 'UP pressed'):
		print(HI)
		plt.axvline(x=time,color='r')
	elif(event[0] is 'RIGHT pressed'):
		print(HI)
		plt.axvline(x=time,color='b')
	elif(event[0] is 'LEFT pressed'):
		print(HI)
		plt.axvline(x=time,color='g')
	elif(event[0] is 'SPACE pressed'):
		plt.axvline(x=time,color='c')
for time, feature0, feature1 in zip(timeList,feature0List,feature1List):
	axs[0,0].plot(time,feature0,c="r")
	axs[1,0].plot(time,feature1,c="g")
	axs[2,0].plot(time,feature0,c="r")
	axs[2,0].plot(time,feature1,c="g")"""

axs[0,0].plot(time_stamps0,EMG0)
axs[1,0].plot(time_stamps0,EMG1)
axs[2,0].plot(time_stamps0,EMG0)
axs[2,0].plot(time_stamps0,EMG1)
#plt.plot(time_stamps0,hEMG0)
#plt.plot(time_stamps0,hEMG1)
plt.show()
