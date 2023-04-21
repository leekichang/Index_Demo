import torch

DEVICE = 'cpu'#cuda' if torch.cuda.is_available() else 'cpu'
ATTACK_TYPES = {"f1":'Normal', "f2":'Reconstruction Attack', "f3":'Adversarial Attack'}