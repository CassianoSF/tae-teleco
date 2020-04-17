import pyaudio

class Mic:
	def __init__(self):
		self.pa = pyaudio.PyAudio()
		self.stream = self.pa.open(
			format = pyaudio.paInt16,
			channels = 1,
			rate = 44100,
			input = True
		)

	def read(self):
		return self.stream.read(int(44100 * 0.05))
