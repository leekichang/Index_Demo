import cv2
import torch
import config as cfg
from SegNet import SegNet
from client import *

# TODO: add train demo

class Attacker:
    def __init__(self):
        self.model = SegNet(n_layers=13, n_class=3)
        self.model.load_state_dict(torch.load('./reconstructor_300.pth', map_location=torch.device(cfg.DEVICE)))
        self.model.eval()
        self.model.to(cfg.DEVICE)
        self.attk_img = np.array(\
                cv2.imread(f'./attack_img.png',\
                cv2.IMREAD_COLOR)/255).transpose(2,0,1)
        
        X = torch.empty((1,3,224,224))
        X[0] = torch.tensor(self.attk_img)
        X = X.to(cfg.DEVICE)
        with torch.no_grad():
            features = self.model.encode(X)
        features = features.to(cfg.DEVICE)
        self.attack_idx = []
        for idx in self.model.indices:
            self.attack_idx.append(idx.to('cpu'))
            
    def train(self):
        pass
    
    def reconstruction_attack(self, data):
        feature, indices, shapes = data['feature'], data['indices'], data['shapes']
        feature = torch.rand(feature.shape).to(cfg.DEVICE)
        
        self.model.set_index(indices, shapes)
        
        for i, index in enumerate(self.model.indices):
            self.model.indices[i] = index.to(cfg.DEVICE)
            
        with torch.no_grad():
            out = self.model.decode(feature)
            out = out.to('cpu').numpy()[0].transpose(1,2,0)
            
        cv2.imshow('Reconstructed Image', out)
        cv2.waitKey(0)
    
    def adversarial_attack(self, data):
        data['indices'] = self.attack_idx
        return data