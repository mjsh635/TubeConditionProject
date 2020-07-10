import sys, platform
import socket
import signal
import time
from contextlib import contextmanager



class DXM300():


    def __init__(self, IP_address = '192.168.1.4', port=50001):
        self.address = (IP_address, port)
        

    def read_status_signals(self):
        return self.send_command(22,'')

    def read_voltage_out(self):
        return self.send_command(19,'')

    def read_current_out(self):
        return self.send_command(19,'')

    def read_filament_current_out(self):
        return self.send_command(19,'')
    
    def set_voltage(self,voltage_to_set):
        """
        :param voltage_to_set: (int) 0 -4095
        """
        self.send_command(10,voltage_to_set)

    def set_current(self,current_to_set):
        """
        :param current_to_set: (int) 0 -4095
        """
        self.send_command(11,current_to_set)
    
    def set_filament_limit(self,fil_limit_to_set):
        """
        :param fil_limit_to_set: (int) 0 -4095
        """
        self.send_command(12,fil_limit_to_set)

    def __enter__(self):
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        print("Attempting to connect...")
        self.socket.connect(self.address)
        

    def __exit__(self, e_type, e_val, e_traceback):
        self.socket.close()

    def connect(self):
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        print("Attempting to connect...")
        self.socket.connect(self.address)

    def disconnect(self):
        self.socket.close()

    def send_command(self, cmd, argm=''):
        """
        :param cmd: 2 ASCII characters representing the command ID

        :param *argm: Command Argument
        """
        if argm != '':
            self.argm = argm + ','
        else:
            self.argm = argm
        try:
            mes = "\x02{0},{1}\x03".format(str(cmd),self.argm).encode("ascii")
            time.sleep(0.5)
            self.socket.send(mes)
            response = self.socket.recv(1024).decode("ascii")
            split_resp = response.split(sep=',')
            return split_resp
        except Exception as e:
            print(e)

# d = DXM300()
# while True:
#     #only run 22 <blank>
#     print("what command and arg?")
#     cmd = input("what command?: ")
#     val = input("what value?: ")
#     with d:
#         print("response:\n",d.send_command(cmd,val))
