from socket import *
import numpy as np
import pickle
import time
import threading
#SERVER_ADDRESS = ('192.168.0.167', 9784)
SERVER_ADDRESS = ('0.0.0.0', 9784)

class Server:
	def __init__(self, server_address) -> None:
		self.server_address = server_address
		self.socket = socket(AF_INET, SOCK_STREAM)
		self.socket.bind(self.server_address)
		self.socket.listen(1)
		print("SERVER IS READY!")
		print('Waiting for a client to connect...')
		self.client_socket, self.client_address = self.socket.accept()
		print(f"CONNECTED BY {self.client_address}")
		msg = "DONE!"
		self.msg_byte = pickle.dumps(msg)
		self.result = None
		self.lock = threading.Lock()

	def recv(self):
		while True:
			try:
				with self.lock:
					result_bytes = b''
					while True:
						data = self.client_socket.recv(1024)
						if not data:
							self.result = None  # set to None to indicate client has disconnected
							break
						result_bytes += data
					self.result = pickle.loads(data)
					print(self.result)
			except:
				pass

	def send(self):
		while True:
			try:
				with self.lock:
					if self.result != None:
						self.client_socket.sendall(self.msg_byte)
						print("MSG SENT!")
						self.result = None
			except:
				pass

	def create_thread(self):
		self.sender = threading.Thread(target=self.send)
		self.sender.daemon = True  #메인프로세스 종료시 같이 종료
		self.receiver = threading.Thread(target=self.recv)
		self.receiver.daemon = True

	def run(self):
		self.create_thread()

		self.sender.start()
		self.receiver.start()
		while True:
			time.sleep(1)
			pass

if __name__ == '__main__':
	server = Server(SERVER_ADDRESS)
	server.run()