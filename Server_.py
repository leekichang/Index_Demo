import threading
import time
from socket import *
import pickle
import config as cfg
from SegNet import SegNet
import torch

import warnings
warnings.filterwarnings(action='ignore')

class Server:
    def __init__(self, SERVER_ADDRESS):
        self.address  = SERVER_ADDRESS
        self.socket   = socket(AF_INET, SOCK_STREAM)
        self.socket.bind(self.address)
        self.socket.listen(1)
        print("server is ready")
        self.client_socket, self.client_addr = self.socket.accept()
        print(f"server connected by {self.client_addr}")
        self.LOCK = threading.Lock()
        self.request = None
        self.connected = True

        self.model = SegNet(n_layers=13, n_class=3)
        self.model.load_state_dict(torch.load('./reconstructor_300.pth', map_location=torch.device(cfg.DEVICE)))
        self.model.eval()
        self.model.to(cfg.DEVICE)

    def compute(self):
        features = self.request['feature']
        indices  = self.request['indices']
        shapes   = self.request['shapes']

        features = features.to(cfg.DEVICE)
        self.model.set_index(indices, shapes)
        for i, index in enumerate(self.model.indices):
            self.model.indices[i] = index.to(cfg.DEVICE)
        with torch.no_grad():
            out = self.model.decode(features)
            out = out.to('cpu').numpy()
        return out

    def send(self):
        while True:
            self.LOCK.acquire()
            if self.request != None and self.request != -1:
                # user_input = int(input('>>>'))
                data = self.compute()
                self.client_socket.send(pickle.dumps(data))
                print(f"DATA SENT: {data.shape}")
                self.request = None
            self.LOCK.release()
    
    def recv(self):
        while True:
            try:
                recv_data = b''
                while True:
                    chunk = self.client_socket.recv(4096)
                    recv_data += chunk
                    if len(chunk) < 4096:
                        break
                # recv_data = self.client_socket.recv(4096)
                result = pickle.loads(recv_data)
                
                if result == -1:
                    self.LOCK.acquire()
                    self.client_socket.close()
                    self.connected = False
                    print("DISCONNECTED")
                    self.connect()
                    self.LOCK.release()
                self.LOCK.acquire()
                print(f"RECEIVCED DATA")
                self.request = result
                self.LOCK.release()
            except:
                pass

    def connect(self):
        print("WAITING FOR NEW CONNECTION")
        self.socket.listen(1)
        self.client_socket, self.client_addr = self.socket.accept()
        print(f"server connected by {self.client_addr}")
        self.is_connected = True

    def create_thread(self):
        self.sender   = threading.Thread(target=self.send)
        self.sender.daemon = True
        self.receiver = threading.Thread(target=self.recv)
        self.sender.daemon = True
    
    def run(self):
        self.create_thread()
        self.sender.start()
        self.receiver.start()
        while True:
            time.sleep(1)
            pass

if __name__ == '__main__':
    SERVER_ADDRESS = ('0.0.0.0', 8080)
    server = Server(SERVER_ADDRESS)
    server.run()