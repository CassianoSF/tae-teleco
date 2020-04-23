import socket, threading, Queue, time

class Server():
	def __init__(self, port):
		host = socket.gethostbyname(socket.gethostname())
		print('Server hosting on IP-> '+str(host))
		sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind((host,port))
		clients = set()
		buff = Queue.Queue()
		print('Server Running...')
		threading.Thread(target=self.recvData,args=(sock,buff)).start()

		while True:
			while not buff.empty():
				time.sleep(0.01)
				data,addr = buff.get()

				if addr not in clients:
					clients.add(addr)
					print(addr, "Connected")

				if data.endswith('qqq'):
					clients.remove(addr)
					print(addr, "Diconnected")
					continue

				for index, c in enumerate(clients):
					try:
						sock.sendto(data, c)
					except:
						pass

	def recvData(self, sock, buff):
		while True:
			try:
				data, addr = sock.recvfrom(4410)
				buff.put((data,addr))
			except:
				pass


server = Server(5000)