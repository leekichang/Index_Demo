#router.py
import cv2
import torch
import pickle
import keyboard
import threading
import numpy as np
from socket import *
from server import *
from client import *
import config as cfg
from SegNet import SegNet

#TODO: Toy Example to Offloading Scenario

ATTACK_TYPES = {"f1":'Normal', "f2":'Reconstruction Attack', "f3":'Adversarial Attack'}
class Receiver(Server):
    def __init__(self, SERVER_ADDRESS):
        super().__init__(SERVER_ADDRESS)
    
    def send(self, data):
        data_byte = pickle.dumps(data)
        self.client_socket.sendall(str(len(data_byte)).encode())

        self.client_socket.sendall(data_byte)
        print(f"DATA SENT")
        print(f"np.shape(data_byte):{np.shape(data_byte)}")
        print(f"len(data_byte):{len(data_byte)}")
    
    def recv(self):
        recv_data = []
        while True: 
            chunk = self.client_socket.recv(4096)
            recv_data.append(chunk)
            if len(chunk) < 4096:
                break
        self.request = pickle.loads(b''.join(recv_data))
        if self.request == 0:
            self.client_socket.close()
            self.connected = False
            print("DISCONNECTED")
            return
        
        print(f"RECEIVCED DATA: {self.request}")

class Sender(Client):
    def __init__(self, SERVER_ADDRESS):
        super().__init__(SERVER_ADDRESS)
    
    def send(self, data):
        self.socket.sendall(pickle.dumps(data))
        print('SENT!')
        if data == 0:
            print("DISCONNECTED!")
            self.connected = False
            self.socket.close()
        

class Router:
    def __init__(self, ROUTER_ADDRESS, SERVER_ADDRESS):
        self.RA, self.SA = ROUTER_ADDRESS, SERVER_ADDRESS
        self.receiver    = Receiver(ROUTER_ADDRESS)
        self.sender      = Sender(SERVER_ADDRESS)
        self.attack_key = "f1"
        self.keyboard_thread = threading.Thread(target=self.keyboard_event_loop)
        self.keyboard_thread.daemon = True
        self.keyboard_thread.start()
        '''
        self.attack_type = "f1", normal routing
        self.attack_type = "f2", reconstruction attack
        self.attack_type = "f3", adversarial attack
        '''
    
    def keyboard_event_loop(self):
        while True:
            event = keyboard.read_event()
            self.key_input = event.name
            if self.key_input in list(ATTACK_TYPES.keys()) and event.event_type == "down":
                self.attack_key = self.key_input
                print(f"{ATTACK_TYPES[self.attack_key]}")
    
    def run(self):
        while True:
            self.receiver.recv()
            if ATTACK_TYPES[self.attack_key] == 'Normal':
                
                if self.receiver.request == 0 \
                    or self.receiver.request == None:
                    self.sender.send(data=self.receiver.request)
                    self.receiver.connect()
                    self.sender.connect()
                    self.receiver.recv()
                self.sender.send(data=self.receiver.request)
                response = self.sender.recv()
                self.receiver.send(data=response)
            elif ATTACK_TYPES[self.attack_key] == 'Reconstruction Attack':
                if self.receiver.request == 0 \
                    or self.receiver.request == None:
                    self.sender.send(data=self.receiver.request)
                    self.receiver.connect()
                    self.sender.connect()
                    self.receiver.recv()
                self.sender.send(data=self.receiver.request)
                response = self.sender.recv()
                self.receiver.send(data=response)
            elif ATTACK_TYPES[self.attack_key] == 'Adversarial Attack':
                if self.receiver.request == 0 \
                    or self.receiver.request == None:
                    self.sender.send(data=self.receiver.request)
                    self.receiver.connect()
                    self.sender.connect()
                    self.receiver.recv()
                self.sender.send(data=self.receiver.request)
                response = self.sender.recv()
                self.receiver.send(data=response)
    

if __name__ == '__main__':
    RA = ('0.0.0.0', 9000)
    SA = ('127.0.0.1', 9002)
    router = Router(RA, SA)
    router.run()