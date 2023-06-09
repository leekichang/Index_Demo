#server.py
import threading
import time
from socket import *
import pickle
import numpy as np
import utils
import torch
import config as cfg
from SegNet import SegNet

class Server:
    def __init__(self, SERVER_ADDRESS):
        self.address  = SERVER_ADDRESS
        self.socket   = socket(AF_INET, SOCK_STREAM)
        self.socket.bind(self.address)
        self.socket.listen(1)
        self.client_socket, self.client_addr = self.socket.accept()
        self.request = None
        self.connected = True
        self.model = None
        
    def set_model(self):
        self.model = SegNet(n_layers=13, n_class=3)
        self.model.load_state_dict(torch.load('./reconstructor_300.pth', map_location=torch.device(cfg.DEVICE)))
        self.model.eval()
        self.model.to(cfg.DEVICE)
    
    def compute(self):
        feature = self.request['feature']
        indices = self.request['indices']
        shapes  = self.request['shapes']
        
        feature = feature.to(cfg.DEVICE)
        
        self.model.set_index(indices, shapes)
        
        for i, index in enumerate(self.model.indices):
            self.model.indices[i] = index.to(cfg.DEVICE)
            
        with torch.no_grad():
            out = self.model.decode(feature)
            out = out.to('cpu').numpy()
        return out
    
    def send(self):
        if self.request != None and self.request != -1:
            data = self.compute()
            data_byte = pickle.dumps(data)
            self.client_socket.sendall(str(len(data_byte)).encode())
            time.sleep(1)
            self.client_socket.sendall(data_byte)
            print(f"DATA SENT")
            print(f"np.shape(data):{np.shape(data)}")
            print(f"len(data_byte):{len(data_byte)}")
            self.request = None
        
    def recv(self):
        data_total_len = int(self.client_socket.recv(4096))
        left_recv_len  = data_total_len
        buffer_size    = 4096
        time.sleep(1)
        
        if data_total_len == -1:
            print("DISCONNECTED!")
            self.connected = False
            return
        
        recv_data = []
        while True:
            chunk = self.client_socket.recv(buffer_size)
            recv_data.append(chunk)
            left_recv_len -= len(chunk)
            if left_recv_len <= 0:
                break
        if not left_recv_len == 0:
            print("Packet Loss!")
        else:
            self.request = pickle.loads(b"".join(recv_data))
            print(f'Received Data:{type(self.request)}\nlen(data):{data_total_len}')
    
    def connect(self):
        print("WAITING FOR NEW CONNECTION")
        self.socket.listen(1)
        self.client_socket, self.client_addr = self.socket.accept()
        print(f"server connected by {self.client_addr}")
        self.connected = True
        
    def run(self):
        while True:
            self.recv()
            self.send()
            if not self.check_connection():self.connect()
    
    def check_connection(self):
        return self.connected

if __name__ == '__main__':
    args = utils.parse_args()
    SERVER_ADDRESS = ('0.0.0.0', args.p)
    print("STARTING")
    server = Server(SERVER_ADDRESS)
    print("CONNECTED")
    server.set_model()
    server.run()