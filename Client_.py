#client.py
import threading
import time
from socket import *
import pickle
import numpy as np
import config as cfg
import torch
from SegNet import SegNet
import cv2
import warnings
warnings.filterwarnings(action='ignore')

class Client:
    def __init__(self, SERVER_ADDRESS):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect(SERVER_ADDRESS)
        print("Client Connected!")
        self.LOCK = threading.Lock()

        self.model = SegNet(n_layers=13, n_class=3)
        self.model.load_state_dict(torch.load('./reconstructor_300.pth', map_location=torch.device(cfg.DEVICE)))
        self.model.to(cfg.DEVICE)
        self.model.eval()

    def compute(self, request):
        img = np.array(cv2.imread(f'./{request}_image.png', cv2.IMREAD_COLOR)/255).transpose(2,0,1)
        X = torch.rand((1,3,224,224))
        X[0] = torch.tensor(img)
        X = X.to(cfg.DEVICE)
        with torch.no_grad():
            features = self.model.encode(X)
        features = features.to(cfg.DEVICE)
        indices = []
        for idx in self.model.indices:
            indices.append(idx.to('cpu'))
        feature_dict = {'feature':features, 'indices':indices, 'shapes':self.model.shapes}
        return feature_dict
    
    def send(self):
        while True:
            try:
                user_input = int(input('>>>'))
                if user_input == -1:
                    self.socket.send(pickle.dumps(user_input))
                    print("DISCONNECT!")
                    break
                data = self.compute(user_input)
                self.socket.send(pickle.dumps(data))
                print('SENT!')
            except:
                break

    def recv(self):
        while True:
            recv_data = b''
            while True:
                chunk = self.socket.recv(4096)
                recv_data += chunk
                if len(chunk) < 4096:
                    break
            if not recv_data:
                print('no receive data')
                break
            print('RECEIVED DATA SHAPE:', pickle.loads(recv_data).shape)

    def create_thread(self):
        self.sender   = threading.Thread(target=self.send)
        self.sender.daemon = True
        self.receiver = threading.Thread(target=self.recv)
        self.sender.daemon = True
    
    def run(self):
        self.create_thread()
        self.sender.start()
        self.receiver.start()
        self.sender.join()
        self.receiver.join()


if __name__ == '__main__':
    SERVER_ADDRESS = ('127.0.0.1', 8080)
    client = Client(SERVER_ADDRESS)
    client.run()