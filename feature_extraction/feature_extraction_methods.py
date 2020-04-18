import numpy as np
import math
import pywt

Fs = 250

entropyWindowSize = 200

#this function merges the three different event types into one merged event vector
def merge_event_lists(space0,space1,space_times,down0,down1,down_times,baseline0,baseline1,baseline_times):
	outEvent0List = []
	outEvent1List = []
	outTimeList = []
	eventTypeList = []
	lenSpace = len(space0)
	lenDown = len(down0)
	lenBaseline = len(baseline0)
	i = j = k = 0
	print(lenSpace,lenDown,lenBaseline)
	while i < lenSpace and j < lenDown and k < lenBaseline:
		print(i,j,k)
		if(space_times[i][0] < down_times[j][0] and space_times[i][0] < baseline_times[k][0]):
			outEvent0List.append(space0[i])
			outEvent1List.append(space1[i])
			outTimeList.append(space_times[i])
			eventTypeList.append('SPACE')
			i += 1
		elif(down_times[j][0] < space_times[i][0] and down_times[j][0] < baseline_times[k][0]):
			outEvent0List.append(down0[j])
			outEvent1List.append(down1[j])
			outTimeList.append(down_times[j])
			eventTypeList.append('DOWN')
			j += 1
		elif(baseline_times[k][0] < space_times[i][0] and baseline_times[k][0] < down_times[j][0]):
			outEvent0List.append(baseline0[k])
			outEvent1List.append(baseline1[k])
			outTimeList.append(baseline_times[k])
			eventTypeList.append('BASELINE')
			k += 1
	while i < lenSpace and j < lenDown:
		if(space_times[i][0] < down_times[j][0]):
			outEvent0List.append(space0[i])
			outEvent1List.append(space1[i])
			outTimeList.append(space_times[i])
			eventTypeList.append('SPACE')
			i += 1
		else:
			outEvent0List.append(down0[j])
			outEvent1List.append(down1[j])
			outTimeList.append(down_times[j])
			eventTypeList.append('DOWN')
			j += 1
	while i < lenSpace and k < lenBaseline:
		if(space_times[i][0] < baseline_times[k][0]):
			outEvent0List.append(space0[i])
			outEvent1List.append(space1[i])
			outTimeList.append(space_times[i])
			eventTypeList.append('SPACE')
			i += 1
		else:
			outEvent0List.append(baseline0[k])
			outEvent1List.append(baseline1[k])
			outTimeList.append(baseline_times[k])
			eventTypeList.append('BASELINE')
			k += 1
	while j < lenDown and k < lenBaseline:
		if(down_times[j][0] < baseline_times[k][0]):
			outEvent0List.append(down0[j])
			outEvent1List.append(down1[j])
			outTimeList.append(down_times[j])
			eventTypeList.append('DOWN')
			j += 1
		else:
			outEvent0List.append(baseline0[k])
			outEvent1List.append(baseline1[k])
			outTimeList.append(baseline_times[k])
			eventTypeList.append('BASELINE')
			k += 1
	while i < lenSpace:
		outEvent0List.append(space0[i])
		outEvent1List.append(space1[i])
		outTimeList.append(space_times[i])
		eventTypeList.append('SPACE')
		i += 1
	while j < lenDown:
		outEvent0List.append(down0[j])
		outEvent1List.append(down1[j])
		outTimeList.append(down_times[j])
		eventTypeList.append('DOWN')
		j += 1
	while k < lenBaseline:
		outEvent0List.append(baseline0[k])
		outEvent1List.append(baseline1[k])
		outTimeList.append(baseline_times[k])
		eventTypeList.append('BASELINE')
		k += 1
	return outEvent0List,outEvent1List,outTimeList,eventTypeList

def rms(wavelet):
	squaredWavelet = np.square(wavelet)
	return math.sqrt(sum(squaredWavelet)/len(wavelet))

def stdev(wavelet):
	avgWavelet = np.mean(wavelet)
	minusAvgWavelet = np.subtract(wavelet,avgWavelet)
	minusAvgSquareWavelet = np.square(minusAvgWavelet)
	return math.sqrt(np.mean(minusAvgSquareWavelet))

def entropy(wavelets):
	meanSquaredList = []
	meanSquaredTotal = []
	j = 0
	for wavelet in wavelets:
		i = 0
		squaredWavelet = np.square(wavelet)
		while i<len(wavelet):
			if(i+199 > len(wavelet)):
				meanSquared = np.mean(squaredWavelet[i:])
			else:
				meanSquared = np.mean(squaredWavelet[i:i+199])
			meanSquaredList.append(meanSquared)
			if(j is 0 or math.floor(i/200)>=len(meanSquaredTotal)):
				meanSquaredTotal.append(meanSquared)
			else:
				meanSquaredTotal[math.floor(i/200)] = meanSquaredTotal[math.floor(i/200)] + meanSquared
			i = i+200
		j = j + 1
	waveEntropy = []
	for meanSquaredEntity in meanSquaredList:
		probs = np.divide(meanSquaredEntity,meanSquaredTotal)
		probsSquared = np.square(probs)
		probsLogged = np.log(probsSquared)
		waveEntropy.append(sum(np.multiply(probsLogged,probsSquared)))
	return waveEntropy

def frequencyMean(frequencies,powers):
	weightedFrequencies = np.sum(np.multiply(frequencies,powers))
	numFrequencies = np.sum(powers)
	return weightedFrequencies / numFrequencies

def frequencyMedian(powers):
	return .5 * sum(powers)

def mmdf(powers):
	sqrtPowers = np.sqrt(powers)
	return .5 * sum(sqrtPowers)

def mmnf(frequencies,powers):
	sqrtPowers = np.sqrt(powers)
	weightedFrequencies = np.sum(np.multiply(frequencies,sqrtPowers))
	numFrequencies = np.sum(sqrtPowers)
	return weightedFrequencies / numFrequencies

def maxMag(rawEMG):
	return max(rawEMG)

def absMeanMag(rawEMG):
	absEMG = np.absolute(rawEMG)
	return np.mean(absEMG)

def absIntMag(rawEMG):
	absEMG = np.absolute(rawEMG)
	return np.trapz(absEMG)

def rawRMS(rawEMG):
	return rms(rawEMG)

def waveform_length(rawEMG):
	i = 1
	sumCoeffs = 0
	while i<(len(rawEMG)):
		sumCoeffs = sumCoeffs + np.abs(rawEMG[i]-rawEMG[i-1])
		i = i + 1
	return sumCoeffs
