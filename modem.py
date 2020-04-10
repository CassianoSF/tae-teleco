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

	def lowpass(self, sig):
		return signal.lfilter(self.low_pass_a, self.low_pass_b, sig)

	def modAmsc(self, sig):
		data = np.fromstring(sig, dtype=np.int16, count=2205)
		amp = data * 100
		filtred = self.lowpass(amp)
		mod = filtred * self.am_carrier
		return mod.astype(np.int16).tobytes()

	def demodAmsc(self, sig):
		data = np.fromstring(sig, dtype=np.int16, count=2205)
		demod = data * self.am_carrier
		print(demod.astype(np.int16))
		return demod.astype(np.int16).tobytes()

	def modAm(self, sig):
		data = np.fromstring(sig, dtype=np.int16, count=2205)
		amp = data * 100
		filtred = self.lowpass(amp)
		mod = filtred * self.am_carrier + self.am_carrier / 2.0
		return mod.astype(np.int16).tobytes()

	def demodAm(self, sig):
		data = np.fromstring(sig, dtype=np.int16, count=2205)
		demod = np.absolute(data, data)
		return demod.astype(np.int16).tobytes()

	def modFm(self, sig):
		data = np.fromstring(sig, dtype=np.int16, count=2205)
		filtred = self.lowpass(data) / 255
		mod = np.zeros_like(filtred)
		phase = 0
		for n in range(0, len(filtred)):
			phase += filtred[n] * np.pi * self.fm_desviation / 44100
			phase %= 2 * np.pi

			i = np.cos(phase)
			q = np.sin(phase)

			carrier = 2 * np.pi * self.fm_carrier_freq * (n / 44100.0)
			mod[n] = (i * np.cos(carrier) - q * np.sin(carrier))			
		return (mod * 32767).astype(np.int16).tobytes()


	def demodFm(self, sig):
		data = np.fromstring(sig, dtype=np.int16, count=2205)
		initial_carrier_phase = random.random() * 2 * math.pi

		last_angle = 0.0
		istream = []
		qstream = []

		mod = np.zeros_like(data, dtype=np.float64)

		for n in range(0, len(data)):
			inputsgn = data[n] / 255
			carrier = 2 * math.pi * self.fm_carrier_freq * (n / 44100.0) + initial_carrier_phase
			istream.append(inputsgn * math.cos(carrier))
			qstream.append(inputsgn * -math.sin(carrier))

		istream = self.lowpass(istream) 
		qstream = self.lowpass(qstream) 

		last_output = 0

		for n in range(0, len(data)):
			i = istream[n]
			q = qstream[n]

			angle = math.atan2(q, i)
			angle_change = last_angle - angle

			if angle_change > math.pi:
					angle_change -= 2 * math.pi
			elif angle_change < -math.pi:
					angle_change += 2 * math.pi
			last_angle = angle

			output = angle_change / (math.pi * self.fm_desviation / 44100)
			if abs(output) >= 1:
					output = last_output
			last_output = output
			
			mod[n] = output
		mod = self.lowpass(mod)
		return (mod * 32767).astype(np.int16).tobytes()