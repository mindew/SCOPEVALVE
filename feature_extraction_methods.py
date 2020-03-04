import numpy as np
import math
import pywt

Fs = 250

entropyWindowSize = 200

def waveform_length(wavelet):
	i = 1
	sumCoeffs = 0
	while i<(len(wavelet)):
		sumCoeffs = sumCoeffs + (wavelet[i]-wavelet[i-1])
		i = i + 1
	return sumCoeffs/len(wavelet)

def mav(wavelet):
	absWavelet = list(map(abs,wavelet))
	return sum(absWavelet)/len(wavelet)

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


