import socket
import numpy as np
import pickle

HOST = ''
PORT = 9999

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST,PORT))
s.listen()

def receive(conn):
	result_bytes = b''
	while True:
		data = conn.recv(1024)
		if not data:
			break
		result_bytes += data

	result = puckle.loads(result_bytes)
	return result

print("server is ready")
while True:
	conn, addr = s.accept()
	print(f'{addr} start!')
	data = receive(conn)
	print(data)
