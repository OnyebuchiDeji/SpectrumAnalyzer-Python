"""
	The goal is to visualize the various frequency spectra
	of an audio file on an Amplitude (y-axis) vs Frequency (x-axis)
	graph --- using a Spectrum Analyzer


	The PyAudio allows one to call a callback function
	to provide sound bytes that will be streamed to the
	device's audio device

	Steps:
		1.	Load Wav file 			- done
		2.	Read frames 			- done
		3.	Send to audio devices  	- done
		4. 	Fast Fourier Analysis 	- done
		5. 	Visualize 				- done

	When creating the bands to visualize the frequencies,
	a logarithmic scaled band was used.
	Also, they are made to be limited between ranges
	100 and 10k hertz
	Hence, `np.logspace(2, 4, num=8)`
	The 2 representes the lower limit 10^2 = 100
	and 4 the upper, 10^4 = 10k
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import array
import pyglet
import pyaudio
import time
import wave


class Renderer(pyglet.window.Window):
	# bands = [1, 2, 3, 4, 5, 6, 7, 8]
	bands = np.logspace(2, 4, num=18)
	#	sample window (group of frames to be processed for frequency splitting)
	frames_per_buffer = 512
	initial_height = 0 # self.height / 2
	height_scaler = 2300
	freq_amplitude = np.array([])
	color = (30, 125, 255)#(255, 125, 30)

	def __init__(self) -> None:
		super().__init__(1200, 675)
		self.batch = pyglet.graphics.Batch()
		self.bars = []
		self.labels = []
		self.v_offset = 125
		self.max_height = self.height - self.v_offset
		self.max_amp = -1
		self.min_amp = -1
		self.mid_amp = -1

		bar_width = self.width / len(self.bands)
		xx = 0
		#	Iterate through the bands
		#	and create a rectangular bar and label for each
		for band in self.bands:
			xx += bar_width * 0.05
			self.bars.append(pyglet.shapes.Rectangle(xx, 0, bar_width * 0.9, self.initial_height,
				color=self.color, batch=self.batch))
			self.labels.append(pyglet.text.Label(str(int(band)), x=xx+bar_width/2, y=self.height - 20,
				anchor_x="center", batch=self.batch))
			xx += bar_width * 0.95

	def start(self, file: wave.Wave_read) -> None:
		#	Generate a list of frequencies that will be analyzed by the fourier transform
		self.frequencies = np.fft.rfftfreq(self.frames_per_buffer, d=1/file.getframerate())

		"""
			The callback is called whenever the sound device
			asks for bytes from the audio stream
			Each time it asks for specifically 512 (self.frames_per_buffer)
			So 512 frames are read from the .wav files

			A frame contains 32 bits of data, 16 for left and 16 for
			right channel.
			One of these bits is a sign bit to allow negative and positive
			values.
			For each frame, a single value that falls between the range:
				-32768 and +32768
			must be acquired.
			So the bytes must be converted to an array of integers (or more specifically,
			signed shorts)
		"""
		def callback(in_data, frame_count: int, time_info, status) -> tuple:
			"""
			Process a number {frame_count} of samples
			So anytime the audio device is ready to eat bytes, this
			is called to read the bytes and send them to the audio device
			"""
			#	Read data grom the .wav file
			data = file.readframes(frame_count)

			#	Convert byte pairs to signed shorts
			array_of_ints = array.array("h", data) 

			#	Only take the left channel from the data by skipping every other
			#	value each iteration of the splice
			left_channel = array_of_ints[::2]

			"""
				Prevents the error:
				    self.freq_amplitude = np.abs(np.fft.rfft(left_channel)) / self.height_scaler
			                             ^^^^^^^^^^^^^^^^^^^^^^^^^
				    output = _raw_fft(a, n, axis, True, True, norm, out=out)
				             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
				in _raw_fft:
	    			raise ValueError(f"Invalid number of FFT data points ({n}) specified.")
				ValueError: Invalid number of FFT data points (0) specified.

			"""
			if len(left_channel) == 0:
				return (b"", pyaudio.paComplete)

			#	Perform fft and store result in a member
			self.freq_amplitude = np.abs(np.fft.rfft(left_channel))#/ self.height_scaler

			"""
			The below scaling was meant to replace the ` np.abs(np.fft.rfft(left_channel)) / self.height_scaler`
			but couldn't because each window has a different maximum amplitude.
			For the sscaling to be proper I need to find the maximum amplitude amongst all
			"""
			# max_amp = max(self.freq_amplitude)
			# self.freq_amplitude = (self.freq_amplitude / (max_amp)) * self.max_height

			#	Better Way:
			temp = self.max_amp
			self.max_amp = max(max(self.freq_amplitude), self.max_amp)
			# self.min_amp = min(self.max_amp, temp)
			self.min_amp = min(max(self.freq_amplitude), self.max_amp)
			#	Instead of midpoint/mean
			# self.mid_amp = (self.max_amp + self.min_amp) / 2.0
			#	Let the value tend more to the min_amp value
			self.mid_amp = (self.max_amp * 0.45 + self.min_amp * 0.55)
			self.freq_amplitude = (self.freq_amplitude / (self.min_amp + 10e-3)) * self.max_height
			# self.max_amp = self.mid_amp

			#	How much data was gotten each window of 512 bytes
			#	You'll see that each window of 512 frames/samples
			#	produces 257 different frequencies
			#	according to the documentation: 
			#	np.fft.rfftfreq returns array of length `n//2 + 1` containing
			#	the sample frequencies. 

			#	There are 257 frequencies in the list
			#	if the space between consecutive frequencies is a band
			#	then there are 256 bands.
			# print(len(self.freq_amplitude))

			return (data, pyaudio.paContinue) #		return data and always continue

		#	Start audio stream and consume
		#	Now stream can be used to control the game loop
		self.audio = pyaudio.PyAudio()
		audio_format = self.audio.get_format_from_width(file.getsampwidth())
		#	this stream runs on a separate thread (non-blocking) in callback mode
		self.stream = self.audio.open(format=audio_format, channels=file.getnchannels(),
							frames_per_buffer=self.frames_per_buffer,
							rate=file.getframerate(), output=True,
							stream_callback=callback) 

		self.last_time = time.perf_counter()
		while self.stream.is_active():
			elapsed_time = time.perf_counter() - self.last_time
			#	Update frequency = 60 times per second
			if elapsed_time > 1 / 60:
				last_time = time.perf_counter()
				#	below is needed to show the window
				#	the try block is needed to stop this main
				#	loop after pyglet's close event runs
				#	it prevents the displaying of errors
				#	and properly breaks the while loop
				try:
					self.dispatch_events()
					self.on_update()
					self.on_draw()
					self.flip()
				except:
					break
		#	Once stream is no longer active
		#	same function that runs upon closing pyglet
		self.on_close()


	def on_update(self) -> None:
		#	Create a list of zeroes. Each frequency band starts with zero.
		#	Bandsa are the columns yhou see on the visualization/screen
		band_bucket = np.zeros(len(self.bands))
		for index, band in enumerate(self.bands):
			start_freq = self.bands[index]
			end_freq = start_freq * 2
			for freq_index in range(len(self.freq_amplitude)):
				#	Put the highest frequency amplitude from the fourier 
				# 	in a matching	band frequency to get the highest
				# frequency value to represent each bucket

				#	First check: does the frequency at the index 
				#   of the correspondingfrequency amplitude
				#	fall within the band?
				if self.frequencies[freq_index] > start_freq and self.frequencies[freq_index] < end_freq:
					#	If it does, is it's amplitude higher than the
					# 	amplitude currently stored in the `band_bucket`?
					#  (Note the band bucket is simply 
					#	holds the amplitude value used for visualization.
					#	this amplitude value thius has to be the highest within that
					#	band to fauthfully represent the band)/
					if self.freq_amplitude[freq_index] > band_bucket[index]:
						band_bucket[index] = self.freq_amplitude[freq_index]

			#	Update the height of the rectangle bar if
			#	the new height in the bucker 
			# is higher than the current height
			if band_bucket[index] > self.bars[index].height:
				self.bars[index].height = band_bucket[index]
			else: #	If not, slowly drop the current height.
				self.bars[index].height /= 1.11


	def on_draw(self) -> None:
		self.clear()
		self.batch.draw()


	def on_key_press(self, symbol, modifiers):
		"""If this is not specified, Esc would also quit the window"""
		if symbol == pyglet.window.key.Q or symbol==pyglet.window.key.ESCAPE:
			self.close()

	def on_close(self):
		# self.start = False
		self.stream.stop_stream()
		self.stream.close()
		self.audio.terminate()
		self.close()
		pyglet.app.exit()


def main_analyze_and_visualize_audio_spectrum(audioPath):
	with wave.open(audioPath, "rb") as file:
		print("Read .wav Audio File: ", os.path.basename(audioPath))

		#	Inspect structural info from wave file
		#	remember, sample width represents frame width
		print("sample_width", file.getsampwidth(), "bytes")
		print("channels", file.getnchannels())
		print("framerate", file.getframerate(), "Hertz")

		Renderer().start(file)


def main():
	#	Main Quest
	#	Analyze audio spectrum
	# main_analyze_and_visualize_audio_spectrum("./_test_audios/beats-my_own.wav")
	main_analyze_and_visualize_audio_spectrum("./_test_audios/audio-ahhhh.wav")


if __name__ == "__main__":
	main()