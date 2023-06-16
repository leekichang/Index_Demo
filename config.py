import torch

DEVICE = 'cpu'#cuda' if torch.cuda.is_available() else 'cpu'
ATTACK_TYPES = {"1":'Normal',
                "2":'Train',
                "3":'Reconstruction Attack',
                "4":'Adversarial Attack'
                }