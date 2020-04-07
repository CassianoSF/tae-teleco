import socket, threading, Queue, sys, random, os, time
import pyaudio, matplotlib, wave, struct, math, numpy
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import collections

class Server():
	def __init__(self, port):
		host = socket.gethostbyname(socket.gethostname())
		print('Server hosting on IP-> '+str(host))
		sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind((host,port))
		clients = set()
		recvPackets = Queue.Queue()
		print('Server Running...')
		self.stop = False
		threading.Thread(target=self.recvData,args=(sock,recvPackets)).start()

		while True:
			time.sleep(0.020)
			while not recvPackets.empty():
				data,addr = recvPackets.get()

				if addr not in clients:
					clients.add(addr)
					print(addr, "Connected")

				print(addr, len(data))

				if data.endswith('qqq'):
					clients.remove(addr)
					print(addr, "Diconnected")
					continue

				for c in clients:
					try:
						sock.sendto(data,c)
					except:
						pass



	def recvData(self, sock, recvPackets):
		while True:
			if self.stop:
				break
			data,addr = sock.recvfrom(4410	)
			recvPackets.put((data,addr))


Server(5000)
