
import pyaudio

class Player():
	def __init__(self):
		p = pyaudio.PyAudio()
		self.stream = p.open(format=pyaudio.paInt16,
			channels=1,
			rate=44100,
			output=True)
				
	def play(self,data):
		self.stream.write(data)

	def stop(self):
		self.stream.stop_stream()
		self.stream.close()