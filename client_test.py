import socket
import numpy as np
import pickle
import threading

from SegNet import SegNet

import warnings

warnings.filterwarnings(action='ignore')

HOST = '192.168.0.167'
PORT = 9784

server_address = (HOST, PORT)

class Client:
    def __init__(self, server_address, feature):
        self.server_address = server_address
        self.socket         = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.feature        = feature

    def connect(self):
        self.socket.connect(self.server_address)


    def disconnect(self):
        self.socket.close()

    def send_request(self):
        while True:
            feature_bytes = pickle.dumps(self.feature)
            self.socket.sendall(feature_bytes)
            print(f"{self.feature} SENT!")
            user_input = input("Enter 'Q' to exit, or press any key")
            if user_input == 'Q':
                break
    def recv_response(self):
        while True:
            response_msg = self.socket.recv(1024)
            response = pickle.loads(response_msg)
            print(response)

    def create_thread(self):
        self.send_thread = threading.Thread(target=self.send_request)
        self.recv_thread = threading.Thread(target=self.recv_response)

    def run(self):
        self.connect()
        self.create_thread()
        self.send_thread.start()
        self.send_thread.join()
#        self.recv_response()
        self.recv_thread.start()
#        self.send_thread.join()
        self.recv_thread.join()
        self.disconnect()


if __name__ == '__main__':
    feature = np.random.rand(5)    
    client = Client(server_address, feature)
    client.run()
