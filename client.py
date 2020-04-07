import socket, threading, Queue, sys, random, os, time
import pyaudio, matplotlib, wave, struct, math, numpy
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import collections

from mic import Mic
from player import Player

from matplotlib.widgets import TextBox
from matplotlib.widgets import Button

class Client():
	def __init__(self):
		client_ip = socket.gethostbyname(socket.gethostname())
		client_port = random.randint(6000,10000)
		self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((client_ip,client_port))
		self.buffers = {}
		self.connected = False
		
	def getBuffers(self):
		return self.buffers
		
	def connect(self, ip, port):
		self.connected = True
		self.server = (ip,port)
		threading.Thread(target=self.recvData,args=(self.sock, lambda : self.connected)).start()
		
	def send(self, data):
		self.sock.sendto(data, self.server)
		
	def disconnect(self):
		self.connected = False
		self.sock.sendto(str('qqq').encode('utf-8'), self.server)
		self.sock.close()
		
	def recvData(self, sock, isConnected):
		while True:
			if not isConnected(): break
			try:
				data,addr = sock.recvfrom(4410)
				if addr in self.buffers:
					count = len(data)/2
					format = "%dh"%(count)
					values =  struct.unpack(format, data)
					for val in values:
						self.buffers[addr].append(val)
				else:
					self.buffers[addr] = collections.deque(maxlen=44100)
			except:
				pass



mic = Mic()
player = Player()
client = Client()
client.connect('192.168.0.20', 5000)
client.send(mic.read())
client.send(mic.read())
ip = '127.0.0.1'
fig = plt.figure()

def sendData(client, mic):
	while True:
		time.sleep(0.001)
		client.send(mic.read())

def animate(i):
	global client
	buffers = client.getBuffers()
	for index, cli in enumerate(buffers):
		_, _, _, im = plt.specgram(buffers[cli], Fs=44100, NFFT=2**10, noverlap=900)
		return im,

def reproduz(client, player):
	while True:
		buffers = client.getBuffers()
		for index, cli in enumerate(buffers):
			data = buffers[cli]
			count = len(data)
			format = "%dh"%(count)
			sound = struct.pack(format, *data)
			player.play(sound)

threading.Thread(target=reproduz, args=(client, player)).start()
threading.Thread(target=sendData, args=(client, mic)).start()
ani = animation.FuncAnimation(fig, animate, interval=1, blit=True)
plt.show()