#router.py

import pickle
import keyboard
import threading
import numpy as np
import config as cfg
from socket   import *
from server   import *
from client   import *
from attacker import *

class C2S(Server):     # Client -> C2S -> Server Forwarding
    def __init__(self, SERVER_ADDRESS):
        super().__init__(SERVER_ADDRESS)
            
    def send(self, data):
        data_byte = pickle.dumps(data)
        self.client_socket.sendall(str(len(data_byte)).encode())
        time.sleep(1)
        self.client_socket.sendall(data_byte)
        self.request = None
    
    def recv(self):
        data_total_len = int(self.client_socket.recv(4096))
        left_recv_len  = data_total_len
        buffer_size    = 4096
        
        if data_total_len == -1:
            self.connected = False
            self.request = -1
            return -1
        
        recv_data = []
        while True:
            chunk = self.client_socket.recv(buffer_size)
            recv_data.append(chunk)
            left_recv_len -= len(chunk)
            if left_recv_len <= 0:
                break
        if not left_recv_len == 0:
            print("Packet Loss!")
        else:
            self.request = pickle.loads(b"".join(recv_data))

class S2C(Client):   # Server -> S2C -> Client Forwarding
    def __init__(self, SERVER_ADDRESS):
        super().__init__(SERVER_ADDRESS)
    
    def recv(self):
        data_total_len = int(self.socket.recv(4096))
        left_recv_len  = data_total_len
        buffer_size    = 4096
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
            return
        else:
            result = pickle.loads(b"".join(recv_data))
            return result
    
    def send(self, data):
        if data == -1:
            self.socket.sendall(str(data).encode())
            self.connected = False
            self.socket.close()
            print("DISCONNECT!")
        else:
            data_byte = pickle.dumps(data)
            self.socket.sendall(str(len(data_byte)).encode())
            time.sleep(1)
            self.socket.sendall(data_byte)

class Router:
    def __init__(self, ROUTER_ADDRESS, SERVER_ADDRESS):
        self.RA, self.SA = ROUTER_ADDRESS, SERVER_ADDRESS
        self.c2s    = C2S(ROUTER_ADDRESS)
        self.s2c    = S2C(SERVER_ADDRESS)
        self.attack_key = "1"
        self.keyboard_thread = threading.Thread(target=self.keyboard_event_loop)
        self.keyboard_thread.daemon = True
        self.keyboard_thread.start()
        self.attacker = Attacker()
        '''
        self.attack_type = "f1", normal routing
        self.attack_type = "f2", train
        self.attack_type = "f3", reconstruction attack
        self.attack_type = "f4", adversarial attack
        '''
    
    def keyboard_event_loop(self):
        while True:
            event = keyboard.read_event()
            self.key_input = event.name
            if self.key_input in list(cfg.ATTACK_TYPES.keys()) and event.event_type == "down":
                self.attack_key = self.key_input
                print(f"{cfg.ATTACK_TYPES[self.attack_key]}")
    
    def attacker_train(self):
        while True:
            if cfg.ATTACK_TYPES[self.attack_key] == 'train':
                print("HELLO WORLD!", flush=True)
        
    def run(self):
        while True:
            self.c2s.recv()
            while self.c2s.request == -1 or self.c2s.request == None:
                self.s2c.send(data=self.c2s.request)
                self.c2s.connect()
                self.s2c.connect()
                self.c2s.recv()
            if cfg.ATTACK_TYPES[self.attack_key] == 'Normal':
                self.s2c.send(data=self.c2s.request)
            elif cfg.ATTACK_TYPES[self.attack_key] == 'Reconstruction Attack':
                # TODO: Implement data revealing
                self.attacker.reconstruction_attack(self.c2s.request)
                self.s2c.send(data=self.c2s.request)
            elif cfg.ATTACK_TYPES[self.attack_key] == 'Adversarial Attack':
                # TODO: Implement data manipulation
                adv_data = self.attacker.adversarial_attack(self.c2s.request)
                self.s2c.send(data=adv_data)
            elif cfg.ATTACK_TYPES[self.attack_key] == 'Train':
                # TODO: Implement data manipulation
                self.s2c.send(data=self.c2s.request)
            response = self.s2c.recv()
            self.c2s.send(data=response)    

if __name__ == '__main__':
    RA = ('0.0.0.0', 9784)
    SA = ('1.233.218.27', 9785)
    router = Router(RA, SA)
    router.run()