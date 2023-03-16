import socket
import numpy as np
import pickle
import threading
import time
from SegNet import SegNet

import warnings

warnings.filterwarnings(action='ignore')

#HOST = '192.168.0.167'
#PORT = 9784
HOST = '127.0.0.1'
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
            try:
                print("SEND?")
                input("Y/N")
                feature_bytes = pickle.dumps(self.feature)
                self.socket.sendall(feature_bytes)
                print(f"{self.feature} SENT!")
                time.sleep(2)
                # user_input = input("Keep communicate? (y/n)")
                # if user_input == 'n':
                #     break
            except:
                pass 


    def recv_response(self):
        while True:
            try:
                response_msg = self.socket.recv(1024)
                response = pickle.loads(response_msg)
                print(response)
            except:
                pass
        

    def create_thread(self):
        self.sender = threading.Thread(target=self.send_request)
        self.sender.daemon = True  #메인프로세스 종료시 같이 종료
        self.receiver = threading.Thread(target=self.recv_response)
        self.receiver.daemon = True

    def run(self):
        self.connect()
        self.create_thread()
        self.sender.start()
        self.receiver.start()
        while True:
            time.sleep(1)
            pass


if __name__ == '__main__':
    feature = np.random.rand(100000)    
    client = Client(server_address, feature)
    client.run()