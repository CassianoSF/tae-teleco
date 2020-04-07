import pyaudio, matplotlib, wave, struct, math, numpy
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import collections


class Mic:
	def __init__(self):
		self.pa = pyaudio.PyAudio()
		self.stream = self.pa.open(
			format = pyaudio.paInt16,
			channels = 1,
			rate = 44100,
			input = True,
			input_device_index = self.getDeviceIndex(),
			frames_per_buffer = int(44100 * 0.05))

	def getDeviceIndex(self):    
		for i in range( self.pa.get_device_count() ):     
			devinfo = self.pa.get_device_info_by_index(i)   
			print( "Dispositivo %d: %s"%(i,devinfo["name"]) )
			if "mic" in devinfo["name"].lower():
				print( "Microfone encontrado: %d - %s" % (i,devinfo["name"]) )
				device_index = i
				return device_index
			if device_index == None:
				raise Exception("Microfone nao encontrado!")

	def read(self):
		return self.stream.read(int(44100 * 0.05))
