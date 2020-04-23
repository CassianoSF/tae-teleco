import matplotlib, socket, random, time
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.widgets import TextBox, Button, Slider
from np_rw_buffer import RingBuffer
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
				data,addr = self.sock.recvfrom(4410)
				values = np.fromstring(data, dtype=np.int16)
				self.buff.read(2205)
				self.buff.write(values)
			except:
				pass

class App():
	def __init__(self):
		self.mic     = Mic()
		self.speaker = Speaker()
		self.client  = Client()
		self.modem   = Modem()

		self.selectedMod = 'AM'

		self.modulations = {
			'AM': self.modem.modAm,
			'AMSC': self.modem.modAmsc,
			'FM': self.modem.modFm
		}

		self.demodulations = {
			'AM': self.modem.demodAm,
			'AMSC': self.modem.demodAmsc,
			'FM': self.modem.demodFm
		}

		self.fig, self.axes = plt.subplots(4, 1, figsize=[6,8])
		plt.subplots_adjust(top=0.7)
		for i in range(4):
			self.axes[i].axes.xaxis.set_visible(False)
			self.axes[i].axes.yaxis.set_visible(False)

		self.input_ip       = TextBox(plt.axes([0.1,  0.05, 0.4, 0.05]), '', initial='192.168.0.20')
		self.btn_connect    =  Button(plt.axes([0.5,  0.05, 0.2, 0.05]), 'Connect')
		self.btn_disconnect =  Button(plt.axes([0.7,  0.05, 0.2, 0.05]), 'Disconnect')

		self.btn_am   =  Button(plt.axes([0.1,  0.94, 0.2, 0.05]), 'AM')
		self.btn_amsc =  Button(plt.axes([0.3,  0.94, 0.2, 0.05]), 'AMSC')
		self.btn_fm   =  Button(plt.axes([0.5,  0.94, 0.2, 0.05]), 'FM')

		self.sld_cutoff     = Slider(plt.axes([0.1,  0.91, 0.7, 0.02]), 'Cutoff',  1.,    2000.,  valinit=1000,   valstep=1.)
		self.sld_order      = Slider(plt.axes([0.1,  0.87, 0.7, 0.02]), 'Order',   2,     50,     valinit=5,      valstep=1)
		self.sld_fm_carrier = Slider(plt.axes([0.1,  0.83, 0.7, 0.02]), 'FM Freq', 3000., 20000., valinit=10000., valstep=100.)
		self.sld_fm_devsiat = Slider(plt.axes([0.1,  0.79, 0.7, 0.02]), 'FM Desv', 300.,  4000.,  valinit=1000.,  valstep=10.)
		self.sld_am_carrier = Slider(plt.axes([0.1,  0.75, 0.7, 0.02]), 'AM Freq', 3000., 20000., valinit=3000.,  valstep=100.)

		self.btn_am.on_clicked(self.selectAM)
		self.btn_amsc.on_clicked(self.selectAMSC)
		self.btn_fm.on_clicked(self.selectFM)

		self.btn_connect.on_clicked(self.connect)
		self.btn_disconnect.on_clicked(self.disconnect)

		self.sld_cutoff.on_changed(self.changeCutoff)
		self.sld_order.on_changed(self.changeOrder)
		self.sld_fm_carrier.on_changed(self.changeFmCarrier)
		self.sld_fm_devsiat.on_changed(self.changeFmDevsiat)
		self.sld_am_carrier.on_changed(self.changeAmCarrier)

		plt.show()

	def selectAM(self, evt):
		self.selectedMod = 'AM'

	def selectAMSC(self, evt):
		self.selectedMod = 'AMSC'

	def selectFM(self, evt):
		self.selectedMod = 'FM'

	def changeCutoff(self, val):
		self.modem.cutoff = val
		self.modem.normal_cutoff = self.modem.cutoff / self.modem.nyq

	def changeOrder(self, val):
		self.modem.order = val

	def changeFmCarrier(self, val):
		self.modem.fm_carrier_freq = val

	def changeFmDevsiat(self, val):
		self.modem.fm_desviation = val

	def changeAmCarrier(self, val):
		self.modem.am_carrier_freq = val


	def connect(self, event):
		self.client = Client()
		self.client.connect(self.input_ip.text)
		Thread(target=self.sendData).start()
		Thread(target=self.playSound).start()
		Thread(target=self.updatePlot).start()

	def disconnect(self, event):
		self.client.disconnect()

	def sendData(self):
		time.sleep(0.01)
		while self.client.isConnected():
			time.sleep(0.01)
			entrada = self.mic.read()
			mod = self.modulations[self.selectedMod](entrada)
			self.client.send(mod)

	def playSound(self):
		time.sleep(0.01)
		while self.client.isConnected():
			time.sleep(0.01)
			data = self.client.getBuffer().get_data().flatten()
			if not len(data): continue
			mod = data[-2205:]
			demod = self.demodulations[self.selectedMod](mod)
			self.speaker.play(demod)


	def updatePlot(self):
		time.sleep(0.01)
		while self.client.isConnected():
			time.sleep(0.01)
			frame = self.client.getBuffer().get_data().flatten()
			data = np.fromstring(frame, dtype=np.int16)
			if not len(data): continue

			self.axes[0].cla()
			self.axes[0].plot(data, color="black")

			self.axes[1].cla()
			self.axes[1].specgram(data, Fs=44100)

			data = self.demodulations[self.selectedMod](frame)
			data = np.fromstring(data, dtype=np.int16)

			self.axes[2].cla()
			self.axes[2].plot(data, color="black")

			self.axes[3].cla()
			self.axes[3].specgram(data, Fs=44100)

			plt.draw()

# matplotlib.rcParams['toolbar'] = 'None'
App()
exit()