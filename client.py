#client.py
import cv2
import torch
import threading
import time
from socket import *
import pickle
import numpy as np
import utils
import config as cfg
from SegNet import SegNet

import warnings
warnings.filterwarnings(action='ignore')

class Client:
    def __init__(self, SERVER_ADDRESS):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect(SERVER_ADDRESS)
        self.connected = True
        print("Client Connected!")
        self.model = SegNet(n_layers=13, n_class=3)
        self.model.load_state_dict(torch.load('./reconstructor_300.pth', map_location=torch.device(cfg.DEVICE)))
        self.model.to(cfg.DEVICE)
        self.model.eval()

    def compute(self, request):
        try:
            img = np.array(\
                cv2.imread(f'./{request}_image.png',\
                cv2.IMREAD_COLOR)/255).transpose(2,0,1)
            print("IMAGE LOADED!")
            X = torch.empty((1,3,224,224))
            X[0] = torch.tensor(img)
            X = X.to(cfg.DEVICE)
            with torch.no_grad():
                features = self.model.encode(X)
            features = features.to(cfg.DEVICE)
            indices = []
            for idx in self.model.indices:
                indices.append(idx.to('cpu'))
            feature_dict = {'feature':features, 'indices':indices, 'shapes':self.model.shapes}
            print("FINISHED LOCAL COMPUTATION")
            return feature_dict
        except:
            print(f"WRONG IMAGE NAME ./{request}_image.png DOESN'T EXIST")
            return -1
    
    def send(self):
        while True:
            user_input = int(input('Enter image number:'))
            if user_input == -1:
                self.socket.sendall(str(user_input).encode())
                self.connected = False
                self.socket.close()
                print("DISCONNECT!")
                break
            else:
                data = self.compute(request=user_input)
                if data == -1:
                    pass
                else:
                    data_byte = pickle.dumps(data)
                    self.socket.sendall(str(len(data_byte)).encode())
                    time.sleep(1)
            
                    self.socket.sendall(data_byte)
                    print(f"DATA SENT")
                    print(f"np.shape(data):{np.shape(data)}")
                    print(f"len(data_byte):{len(data_byte)}")
                    break

    def recv(self):
        data_total_len = int(self.socket.recv(1024))
        left_recv_len  = data_total_len
        buffer_size    = 16384
        time.sleep(1)

        recv_data = []
        while True:
            chunk = self.socket.recv(buffer_size)
            recv_data.append(chunk)
            left_recv_len -= len(chunk)
            if left_recv_len <= 0:
                break
        if not left_recv_len == 0:
            print("Packet Loss!")
        else:
            result = pickle.loads(b"".join(recv_data))
            print(f'받은 데이터:{result.shape}\n{data_total_len}')
    
    def run(self):
        while True:
            self.send()
            if not self.check_connection():break
            self.recv()
            if not self.check_connection():break

    def check_connection(self):
        return self.connected

if __name__ == '__main__':
    args = utils.parse_args()
    SERVER_ADDRESS = (args.ip, args.p)
    client = Client(SERVER_ADDRESS)
    client.run()


