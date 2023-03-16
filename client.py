import cv2

import torch
import socket
import numpy as np
import pickle
import config as cfg

from SegNet import SegNet

import warnings
warnings.filterwarnings(action='ignore')

model = SegNet(n_layers=13, n_class=3)
model.load_state_dict(torch.load('./reconstructor_300.pth', map_location=torch.device(cfg.DEVICE)))
model.to(cfg.DEVICE)
model.eval()
np.random.seed(20000811)

HOST = '192.168.0.14'
PORT = 9004

def send(features):
    #features = np.array(features)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    features_bytes = pickle.dumps(features)#.tobytes()
    s.sendall(features_bytes)
    s.close()

# features = np.random.randn(1,10)

#img = cv2.imread('./0_image.png', cv2.IMREAD_COLOR)
img_ = np.array(cv2.imread('./0_image.png', cv2.IMREAD_COLOR)/255).transpose(2,0,1)

#cv2.imshow('image', img)
#cv2.waitKey(0)
#cv2.destroyAllWindows()

X = torch.rand((1,3,224,224))
X[0] = torch.tensor(img_)
X = X.to(cfg.DEVICE)

with torch.no_grad():
    features = model.encode(X)
features = features.to(cfg.DEVICE)
# print(features.shape)

indices = []

for idx in model.indices:
    indices.append(idx.to(cfg.DEVICE))

feature_dict = {'feature':features, 'indices':indices, 'shapes':model.shapes}

# send(features.numpy())
send(feature_dict)
# print(feature)

# print(feature.shape)
