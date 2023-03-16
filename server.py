import torch
import socket
import numpy as np
import pickle
import cv2
import config as cfg

from SegNet import SegNet

model = SegNet(n_layers=13, n_class=3)
model.load_state_dict(torch.load('./reconstructor_300.pth', map_location=torch.device(cfg.DEVICE)))
model.eval()
model = model.to(cfg.DEVICE)

HOST = '0.0.0.0'
PORT = 9784
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (HOST, PORT)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

def receive_features(client_socket):
    result_bytes = b''
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        result_bytes += data

    result = pickle.loads(result_bytes)
    features = result['feature']
    indices  = result['indices']
    shapes   = result['shapes']
    return features, indices, shapes

msg = 'DONE!'
msg_bytes = pickle.dumps(msg)

print("Server is ready!")
while True:
	client_socket, client_address = server_socket.accept()
	print('Connected by', client_address)
	features, indices, shapes = receive_features(client_socket)
	print("RECEIVCED THE FEATURES START OPERATION")
        
	features = features.to(cfg.DEVICE)
	model.set_index(indices, shapes)
	for i, index in enumerate(model.indices):
		model.indices[i] = index.to(cfg.DEVICE)
	with torch.no_grad():
		out = model.decode(features)
		out = out.to('cpu').numpy()
	# img = out[0].transpose(1,2,0)*255
	# cv2.imwrite('./result.png', img)
	# img = cv2.imread('./result.png')
	print(f'server side operation for {client_address} is done')
	client_socket.sendall(msg_bytes)
	print("Sent check msg")
	client_socket.close()