"""
	The goal is to visualize the various frequency spectra
	of an audio file on an Amplitude (y-axis) vs Frequency (x-axis)
	graph --- using a Spectrum Analyzer


	But in an audio file (.wav), the y-axis is the amplitude
	and the x-axis is time. At every given moment, there is an
	amplitude whose value is a combination of all the frequencies
	at that moment.

	This complex combination of frequencies is what uniquely characterises sounds.

	At each time there is an amplitude made out of many different frequencies

	A Spectrum Analyzer is used to visualize all the frequencies of an amplitude
	at a given time. This can also be said as all the frequencies of the audio
	at a single time frame.

	But how do you separate the different frequencies that exist in the audio
	at a particular time frame? Using the Fourier Transform.

	Now, a spectrum is a collection of things that make up a continuum

	In the final visualization, the continuum is the niquist frequency range
	which will be broken up in bands of sub frequencies that together form 
	a spectrum 
"""
import sys
import numpy as np
import matplotlib.pyplot as plt

def case1_splitting_frequencies():
	"""
	#	Case 1 - Splitting Frequencies	
	
	Demonstrates the use of the Fast Fourier Transform
	algorithm in numpy to split the frequency of a simple
	multi-frequenct waveform

	A .wav file is a collection of samples.
	A sample is called a frame.
	In a standard .wav file, each frame contains 32 bits of information
	16 bits represent the left and right channels of audio each --- making up 32 bits.

	Frames exist for each moment of time, contianing the amplitude information.
	The amplitude information for each frame have a combination of frequencies.

	How can these individual frequencies be gotten from a SINGLE frame? It can not.

	However, one can indeed extract them from a COLLECTION of frames by utilizing the
	Fourier Transform method.

	This COLLECTION of frames is called a WINDOW.

	The size of the window is customizable. For background sound, a large window
	can be used to get the spectrum of frequencies in it.

	But for fast-moving audio which as a result have a much larger range of frequencies,
	it is best to analyze their frequencies using small windows.

	In this implementation, a window can also be called the framelength --- e.g. number of bytes
	of frames to analyze

	Also, in this demonstration, a signal can also be called a note, since the sine waves
	represent the sound from a single musical note 

	"""

	samplerate = 44100
	rootnote = 800 		#	A-note, 880Hz
	framelength = 512	#	window size

	times = np.arange(framelength)

	#	first wave -- simple sine wave signal of note A
	#	times / samplerate is done because sameple rate is the no. of frames per second
	#	so `times / samplerate` properly scales the value according to intended samplerate
	signal1 = np.sin(2 * np.pi * rootnote * times / samplerate)

	# amplitudes = signal1
	# plt.title("Single-Note Sine Wave (A)")
	#	plot(x-points, y-points)
	#	graphing amplitudes from signal1 with time
	# plt.plot(times, amplitudes)
	# plt.show()


	secondnote = rootnote * 4 #	A higher octave frequency of note A
	signal2 = np.sin(2 * np.pi * secondnote * times / samplerate) * 0.5 	#	Half Amplitude == Half Volumne

	#	A more complex wave
	amplitudes = (signal1 + signal2 ) / 2
	# plt.title("Two-Note Sine Wave")
	# plt.plot(times, amplitudes)
	# plt.show()


	#	Extracting Individual Frequencies with Fourier Transform

	#	Horizontal(X) axis from -samplerate/2 to samplerate/2
	frequencies = np.fft.fftfreq(framelength, d=1/samplerate)

	#	Positive Frequency Amplitudes only
	freq_amplitudes = np.abs(np.fft.fft(amplitudes))

	"""
	You'll see the different frequencies visible but the image mirrored
	This symmetty is called FOLDING
	Note how the frequencies (x-axis) are in the range -22050 to +22050
	This '22050' is half of the sample frequency (44100) and is called
	the Niquist or Folding frequency

	To allow a good, non-distorted signal, one must double the sample
	frequency of the spectrum one is trying to capture.
	That is, in audio processing, we are trying to capture the 
	human hearing range/spectrum, which is about '22khz' or '22000hz, that is
	why most audios' sample frequency is determined to be "44100"
	(double the intended spectrum).

	One always needs to double the sample frequency of the niquist frequency
	to prevent signal distortion.

	Since one only needs one side of the mirrored graph image, one can obtain
	just the right part of the image.
	"""
	# plt.title("Fourier Individual Frequencies - Mirrored")
	# plt.plot(frequencies, freq_amplitudes)
	# plt.show()


	#	Get only the right-side of the diagram
	#	Horizontal axis from 0 to samplerate/2
	frequencies2 = np.fft.rfftfreq(framelength, d=1/samplerate)
	#	Positive Frequency Amplitudes
	freq_amplitudes2 = np.abs(np.fft.rfft(amplitudes))
	"""
		Notice the two frequencies

		One's peak is around 120 and the other around 60
	"""
	plt.title("Fourier Individual Frequencies - Positive")
	plt.plot(frequencies2, freq_amplitudes2)
	plt.show()


def main():
	#	Splitting Frequencies
	case1_splitting_frequencies()


if __name__ == "__main__":
	main()