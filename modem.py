from scipy import signal
import numpy as np
import random
import math
# import code; code.interact(local=dict(globals(), **locals()))

class Modem():
	def __init__(self):
		self.order = 20
		self.fs = 44100
		self.cutoff = 1000.
		self.nyq = self.fs / 10.
		self.normal_cutoff = self.cutoff / self.nyq
		self.am_carrier_freq = 3000.
		self.fm_carrier_freq = 10000.
		self.fm_desviation = 1000.

	def lowPass(self, sig):
		low_pass_a, low_pass_b = signal.butter(self.order, self.normal_cutoff, btype='low', analog=False)
		return signal.lfilter(low_pass_a, low_pass_b, sig)

	def am_carrier(self, data):
		return np.cos(2*np.pi * np.arange(len(data)) * self.am_carrier_freq / self.fs)

	def fm_carrier(self, data):
		return ([
			np.cos(2*np.pi * np.arange(len(data)) * self.fm_carrier_freq / self.fs),
			np.sin(2*np.pi * np.arange(len(data)) * self.fm_carrier_freq / self.fs)
		])
	
	def modAmsc(self, sig):
		data = np.fromstring(sig, dtype=np.int16)
		amp = data * 100
		filtred = self.lowPass(amp)
		mod = filtred * self.am_carrier(data)
		return mod.astype(np.int16).tobytes()

	def demodAmsc(self, sig):
		data = np.fromstring(sig, dtype=np.int16)
		demod = data * self.am_carrier(data)
		return demod.astype(np.int16).tobytes()

	def modAm(self, sig):
		data = np.fromstring(sig, dtype=np.int16)
		amp = data * 100
		filtred = self.lowPass(amp)
		am_carrier = self.am_carrier(data)
		mod = filtred * am_carrier + am_carrier / 2.0
		return mod.astype(np.int16).tobytes()

	def demodAm(self, sig):
		data = np.fromstring(sig, dtype=np.int16)
		demod = np.absolute(data, data)
		demod = self.lowPass(demod)
		return demod.astype(np.int16).tobytes()

	def modFm(self, sig):
		data = np.fromstring(sig, dtype=np.int16)
		filtred = self.lowPass(data) / 255
		phase = np.cumsum((filtred * np.pi * self.fm_desviation / 44100) % (2 * np.pi))
		fm_carrier_cos, fm_carrier_sin = self.fm_carrier(data)
		i = np.cos(phase) * fm_carrier_cos
		q = np.sin(phase) * fm_carrier_sin
		mod = (i - q) * 32767
		return mod.astype(np.int16).tobytes()

	def demodFm(self, sig):
		data = np.fromstring(sig, dtype=np.int16)
		fm_carrier_cos, fm_carrier_sin = self.fm_carrier(data)
		istream = self.lowPass(fm_carrier_cos * data)
		qstream = self.lowPass(fm_carrier_sin * data)
		angle = np.arctan2(qstream, istream)
		angle[1:] -= angle[:-1]
		angle[angle > np.pi] -= 2 * np.pi
		angle[angle < -np.pi] += 2 * np.pi
		output = angle / (math.pi * self.fm_desviation / 44100)
		return (output * 32767).astype(np.int16).tobytes()