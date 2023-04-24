import torch

DEVICE = 'cpu'#cuda' if torch.cuda.is_available() else 'cpu'
ATTACK_TYPES = {"f1":'Normal',
                "f2":'Train',
                "f3":'Reconstruction Attack',
                "f4":'Adversarial Attack'
                }