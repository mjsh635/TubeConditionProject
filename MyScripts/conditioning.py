"""this class will handle conditioning with the different types of power supplies
"""
import time,datetime
import pathlib, sys
import threading

# Logger_1.append_to_log(f"""[Manual KV/MA Adjustment, 
#         set target KV: {request.form["kvSet"]} 
#         set target KV: {request.form["mASet"]}
#         {datetime.datetime.today()}]""")


class conditioning_Controller():
    def __init__(self, HVSupply=None, Logger=None, HVSettings=None):
        """
        :param HVSupply: (DXM Supply) supply to control

        :param Logger: (File Logger) file to make log notes in

        :HVSettings: (dict of settings) settings to be used for the routine
        """
        self.records = {
            "date" : "",
            "tubeSNum" : "",
            "supplyModel" : "",
            "maxLvlsReached" : [0.0,0.0],
            "timeAtMax" : [0.0,0.0],
            "totalCondTime" : 0,
            "numMaxRamps" : 0,
            "avgFilCur" : 0.0
        }
        self.HV = HVSupply
        self.settings = HVSettings
        self.Log = Logger
        self.CondStarted = False
        self.kill_sig = threading.Event()
        
        

    def start_cycle(self):
        # Start the cycle
        self.kill_sig.clear()
        self.cond_thread = threading.Thread(target=self.__conditioning)
        self.cond_thread.start()

    def stop_cycle(self):
        # Set the kill_sig to end the conditioning routine
        self.kill_sig.set()
    
    def __conditioning(self):
        # Code that handles the conditioning routine
        print("Conditioning.",end='')
        self.CondStarted = True
        while not self.kill_sig.is_set():
            print(".",end='')
            time.sleep(0.5)  
        self.CondStarted = False
        print(" Done")
        self.Log.append_to_log(self.records)

            
