import numpy as np
import socket
import pickle

HOST = '1.233.219.178'
PORT = 9999

def send(data):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    data_bytes = pickle.dumps(data)
    s.sendall(data_bytes)
    s.close()

data = np.random.rand(10)
print(data)
send(data)
