import pyaudio

class Speaker():
	def __init__(self):
		p = pyaudio.PyAudio()
		self.stream = p.open(
			format=pyaudio.paInt16,
			channels=1,
			rate=44100,
			output=True, 
			frames_per_buffer = int(44100 * 0.05)
		)
				
	def play(self,data):
		self.stream.write(data)

	def stop(self):
		self.stream.stop_stream()
		self.stream.close()