from scipy import signal
import numpy as np
import random
import math
# import code; code.interact(local=dict(globals(), **locals()))

class Modem():
	def __init__(self):
		order = 2
		fs = 44100
		cutoff = 500
		nyq = fs / 10.0 # <<- Minimo 2.0
		normal_cutoff = cutoff / nyq
		am_carrier_freq = 3000
		self.fm_carrier_freq = 10000.0
		self.fm_desviation = 1000.0
		self.low_pass_a, self.low_pass_b = signal.butter(order, normal_cutoff, btype='low', analog=False)
		self.am_carrier = np.cos(2*np.pi * np.arange(fs * 0.05) * am_carrier_freq / fs)
		self.fm_carrier_cos = np.cos(2*np.pi * np.arange(fs * 0.05) * self.fm_carrier_freq / fs)
		self.fm_carrier_sin = np.sin(2*np.pi * np.arange(fs * 0.05) * self.fm_carrier_freq / fs)

	def lowpass(self, sig):
		return signal.lfilter(self.low_pass_a, self.low_pass_b, sig)

	def modAmsc(self, sig):
		data = np.fromstring(sig, dtype=np.int16)
		amp = data * 100
		filtred = self.lowpass(amp)
		mod = filtred * self.am_carrier
		return mod.astype(np.int16).tobytes()

	def demodAmsc(self, sig):
		data = np.fromstring(sig, dtype=np.int16)
		demod = data * self.am_carrier
		return demod.astype(np.int16).tobytes()

	def modAm(self, sig):
		data = np.fromstring(sig, dtype=np.int16)
		amp = data * 100
		filtred = self.lowpass(amp)
		mod = filtred * self.am_carrier + self.am_carrier / 2.0
		return mod.astype(np.int16).tobytes()

	def demodAm(self, sig):
		data = np.fromstring(sig, dtype=np.int16)
		demod = np.absolute(data, data)
		return demod.astype(np.int16).tobytes()

	def modFm(self, sig):
		data = np.fromstring(sig, dtype=np.int16)
		filtred = self.lowpass(data) / 255
		phase = np.cumsum((filtred * np.pi * self.fm_desviation / 44100) % (2 * np.pi))
		i = np.cos(phase) * self.fm_carrier_cos
		q = np.sin(phase) * self.fm_carrier_sin
		mod = (i - q) * 32767
		return mod.astype(np.int16).tobytes()

	def demodFm(self, sig):
		data = np.fromstring(sig, dtype=np.int16)
		istream = self.lowpass(self.fm_carrier_cos * data) 
		qstream = self.lowpass(self.fm_carrier_sin * data) 
		angle = np.arctan2(qstream, istream)
		angle[1:] -= angle[:-1]
		angle[angle > np.pi] -= 2 * np.pi
		angle[angle < -np.pi] += 2 * np.pi
		output = angle / (math.pi * self.fm_desviation / 44100)
		return (output * 32767).astype(np.int16).tobytes()