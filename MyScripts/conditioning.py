"""this class will handle conditioning with the different types of power supplies
"""
import time,datetime
import pathlib, sys
import threading

class conditioning_Controller():
    def __init__(self, HVSupply=None, Logger=None, HVSettings=None):
        """
        :param HVSupply: (DXM Supply) supply to control

        :param Logger: (File Logger) file to make log notes in

        :HVSettings: (dict of settings) settings to be used for the routine
        """
        self.HV = HVSupply
        self.settings = HVSettings
        self.Log = Logger
        self.CondStarted = False

    def start_cond(self):
        self.cond_thread = threading.Thread(self.__conditioning(),)
        self.CondStarted = True
    
        self.cond_thread.start()

    def stop_cond(self):
        print("ended")
        self.cond_thread.join()
        

    def __conditioning(self):
        while True:
            print("conditioning")
            time.sleep(2)


c = conditioning_Controller()

c.start_cond()

time.sleep(5)

c.stop_cond()