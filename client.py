# python interface.py
import pyaudio, matplotlib, socket, random, time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

from matplotlib.widgets import TextBox
from matplotlib.widgets import Button

from np_rw_buffer import RingBuffer
from multiprocessing import Process
from threading import Thread

from mic import Mic
from speaker import Speaker
from modem import Modem

class Client():
	def __init__(self):
		client_ip = socket.gethostbyname(socket.gethostname())
		client_port = random.randint(6000,10000)
		self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((client_ip,client_port))
		self.buff = RingBuffer((4410 * 10), dtype=np.int16)
		self.buff.write([0] * (4410 * 10))
		self.connected = False
		
	def getBuffer(self):
		return self.buff

	def isConnected(self):
		return self.connected
		
	def connect(self, ip, port=5000):
		self.connected = True
		self.server = (ip,port)
		Thread(target=self.recvData).start()
		
	def send(self, data):
		self.sock.sendto(data, self.server)
		
	def disconnect(self):
		self.connected = False
		time.sleep(0.1)
		self.sock.sendto(str('qqq').encode('utf-8'), self.server)
		self.sock.close()
		
	def recvData(self):
		while self.connected:
			try:
				data,addr = self.sock.recvfrom(4412)
				values = np.fromstring(data, dtype=np.int16)
				self.buff.read(2205)
				self.buff.write(values)
			except:
				pass

class App():
	def __init__(self):
		self.fig, self.axes = plt.subplots(6, 1, figsize=[6,8])
		for i in range(6):
			self.axes[i].axes.xaxis.set_visible(False)
			self.axes[i].axes.yaxis.set_visible(False)

		self.input_ip       = TextBox(plt.axes([0.1,  0.05, 0.4, 0.05]), '', initial='192.168.0.20')
		self.btn_connect    =  Button(plt.axes([0.5,  0.05, 0.2, 0.05]), 'Connect')
		self.btn_disconnect =  Button(plt.axes([0.7,  0.05, 0.2, 0.05]), 'Disconnect')
		self.btn_connect.on_clicked(self.connect)
		self.btn_disconnect.on_clicked(self.disconnect)
		self.mic     = Mic()
		self.speaker = Speaker()
		self.client  = None
		self.anim    = None
		self.modem   = Modem()
		plt.show()

	def connect(self, event):
		self.client = Client()
		self.client.connect(self.input_ip.text)
		Thread(target=self.sendData).start()
		Thread(target=self.playSound).start()
		Thread(target=self.updatePlot).start()

	def disconnect(self, event):
		self.client.disconnect()
		# self.anim.event_source.stop()

	def sendData(self):
		time.sleep(0.01)
		while self.client.isConnected():

			entrada = self.mic.read()
			mod = self.modem.modFm(entrada)
			self.client.send(mod)

	def playSound(self):
		time.sleep(0.01)
		while self.client.isConnected():
			data = self.client.getBuffer().get_data().flatten()
			print(len(data))
			if not len(data): continue
			mod = data[-2205:]
			demod = self.modem.demodFm(mod)
			self.speaker.play(demod)


	def updatePlot(self):
		time.sleep(0.01)
		while self.client.isConnected():
			data = self.client.getBuffer().get_data().flatten()
			data = np.fromstring(data, dtype=np.int16, count=(4410 * 10))
			self.axes[0].cla()
			self.axes[0].plot(data, color="black")

			# self.axes[0].cla()
			# self.axes[0].specgram(data, Fs=44100, window=np.blackman, NFFT=2**10, overlaps=900)

			plt.draw()

matplotlib.rcParams['toolbar'] = 'None'
App()
exit()