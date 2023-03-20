import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Socket Programming')
    parser.add_argument('--ip', default='192.168.0.167', type=str)
    parser.add_argument('--p', default=9784, type=int)
    args = parser.parse_args()
    return args