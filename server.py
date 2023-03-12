import torch
import socket
import numpy as np
import pickle
import cv2

from SegNet import SegNet

HOST = '127.0.0.1'
PORT = 9999

model = SegNet(n_layers=13, n_class=3)
model.load_state_dict(torch.load('./reconstructor_300.pth'))
model.eval()
model = model.to('cuda')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()

def receive_features(conn):
    #all_features = []
    #all_indices  = []
    result_bytes = b''
    while True:
        data = conn.recv(1024)
        if not data:
            break
        result_bytes += data

    result = pickle.loads(result_bytes)
    features = result['feature']
    indices  = result['indices']
    shapes   = result['shapes']
    return features, indices, shapes
    #all_features.extend(features)
    #all_indices.extend(indices)
    #return all_features, all_indices

print("Server is ready!")
while True:
    conn, addr = s.accept()
    print('Connected by', addr)
    features, indices, shapes = receive_features(conn)
    features = features.to('cuda')
    model.set_index(indices, shapes)
    for i, index in enumerate(model.indices):
        model.indices[i] = index.to('cuda')
    with torch.no_grad():
        out = model.decode(features)
        out = out.to('cpu').numpy()
    img = out[0].transpose(1,2,0) * 255
    cv2.imwrite('./result.png', img)
    print(f'server side operation for {addr} is done')
    conn.close()



