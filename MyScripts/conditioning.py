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
            "startDate" : "",
            "endDate" : "",
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
        self.cond_thread = threading.Thread(target=self.__oldconditioning)
        self.cond_thread.start()

    def stop_cycle(self):
        # Set the kill_sig to end the conditioning routine
        self.kill_sig.set()
    
    def __oldconditioning(self):
        # Code that handles the conditioning routine
        print("Conditioning.",end='')
        self.CondStarted = True
        while not self.kill_sig.is_set():
            print(".",end='')
            time.sleep(0.5)  
        self.CondStarted = False
        print(" Done")
        self.Log.append_to_log(self.records)

    def __conditioning(self):
        """The algorithm for the conditioning of tubes
        """
        """self.settings = {
                        "tubeSNum" : "",
                        "filCurLim" : 0.0,
                        "filPreHeat" : 0.0,
                        "condKVStart" : 0.0,
                        "condKVTarget" : 0.0,
                        "condMAStart" : 0.0,
                        "condMATarget" : 0.0,
                        "condStepDwell" : 0.0,
                        "condPostArcDwell" : 0.0,
                        "condAtMaxDwell : 0.0,
                        "condOffDwell" : 0.0,
                        "condStepCount" : 0.0,
                        "maxKV" : 0.0,
                        "maxMA" : 0.0      
                        }
        """
        def setup():
            # set Filament Current Limit and Log it
            self.HV.set_filament_limit(self.settings["filCurLim"])
            self.Log.append_to_log((f"""[Conditiong Mode, 
            Filament Current Limit: {self.settings["filCurLim"]} 
            {datetime.datetime.today()}]"""))

            # set Filament Preheat and log it
            self.HV.set_filament_limit(self.settings["filPreHeat"])
            self.Log.append_to_log((f"""[Conditiong Mode,
            Filament Preheat Set  : {self.settings["filPreHeat"]}
            {datetime.datetime.today()}]"""))    
            self.start_time = datetime.datetime.now()
            self.records["startDate"] = datetime.date.today
            self.CondStarted = True
            self.condStepCount = self.settings["condStepCount"]
            self.condKVTarget = self.settings["condKVTarget"]
            self.condKVStart = self.settings["condKVStart"]
            self.condMATarget = self.settings["condMATarget"]
            self.condMAStart = self.settings["condMAStart"]
            self.condPostArcDwell = self.settings["condPostArcDwell"]
            self.condOffDwell = self.settings["condOffDwell"]
            self.kvStepSize = (self.condKVTarget - self.condKVStart)/self.condStepCount
            self.maStepSize = (self.condMATarget - self.condMAStart)/self.condStepCount
            self.condStepDwell = self.settings["condStepDwell"]
            self.condAtMaxDwell = self.settings["condAtMaxDwell"]
            self.maxKVReached = 0.0
            self.maxMAReached = 0.0
            self.kvTimeAtMax = 0.0
            self.maTimeAtMax = 0.0
            self.numMaxRamps = 0
            self.avgFilCur = 0.0
            self.currentKVset = self.settings["condKVStart"]
            self.currentMAset = self.settings["condMaStart"]
            self.currentMAsetArced = self.currentMAset
            self.currentStepNumber = 0
            self.runKVLoop = True

        def tearDown():
            self.HV.xray_off()
            self.end_time = datetime.datetime.now()
            self.records["totalCondTime"] = self.end_time - self.start_time
            self.records["endDate"] = datetime.date.today()
            self.CondStarted = False
            self.records["tubeSNum"] = self.settings["tubeSNum"]
            self.records["supplyModel"] = self.HV.model
            self.records["maxLvlsReached"] = [self.maxKVReached, self.maxMAReached]
            self.records["timeAtMax"] = [self.kvTimeAtMax, self.maTimeAtMax]
            self.records["numMaxRamps"] = self.numMaxRamps
            self.records["avgFilCur"] = self.avgFilCur

        setup()
        while not self.kill_sig.is_set():
            # Conditioning Algo here
            if ((self.currentKVset <= self.condKVTarget) and self.runKVLoop):
                self.HV.set_voltage(self.currentKVset)
                self.HV.set_current(self.currentMAset)
                while ((datetime.datetime.now() < datetime.timedelta(minutes=self.condStepDwell)) and (not self.kill_sig.is_set())):
                    if self.HV.is_ArcPresent():
                        if self.currentStepNumber == 0:
                            self.currentMAsetArced += 1
                            if self.HV.is_emitting():
                                self.HV.set_current(self.currentMAsetArced)
                            else:
                                self.HV.set_current(self.currentMAsetArced)
                                self.HV.xray_on()
                        
                    else:
                        time.sleep(1)
                #update maxs and step
                self.maxKVReached = self.currentKVset
                self.currentStepNumber += 1
                #set KV to next value
                self.currentKVset += self.kvStepSize
                self.HV.set_voltage(self.currentKVset)

            else:
                #you've reached 1 on the graph at this point
                self.currentKVset = self.currentKVset * 0.75
                self.runKVLoop = False
                self.HV.set_voltage = (self.currentKVset)
                self.currentMAset = self.currentMAset + self.maStepSize
                self.currentStepNumber = 0

            if self.currentMAset <= self.condMATarget:
                self.HV.set_current(self.currentMAset)
                while ((datetime.datetime.now() < datetime.timedelta(minutes=self.condStepDwell)) and not self.kill_sig.is_set()) :
                    if self.HV.is_ArcPresent():
                        pass
                        # if self.currentStepNumber == 0:
                        #     if self.HV.is_emitting():
                        #         pass
                        #     else:
                        #         self.HV.xray_on()
                        
                        #     self.currentMAsetArced += 1
                        #     self.HV.set_current(self.currentMAsetArced)
                    else:
                        time.sleep(1)
                #update maxs and step
                self.maxMAReached = self.currentMAset
                self.currentStepNumber += 1
                #set KV to next value
                self.currentMAset += self.maStepSize
            else:
                #you've reached 2 on the graph at this point
                pass

            for loop in range (4):
                if not self.kill_sig.is_set():
                    while ((datetime.datetime.now() < datetime.timedelta(minutes=self.condAtMaxDwell)) and not self.kill_sig.is_set()): 
                        # powered max dwell if here 3
                        if self.HV.is_ArcPresent():
                                pass
                                
                        else:

                            time.sleep(1)

                    self.HV.xray_off()
                    while ((datetime.datetime.now() < datetime.timedelta(minutes=self.condOffDwell)) and not self.kill_sig.is_set()):
                        # powered off dwell if here 4
                        time.sleep(1)

                    self.HV.xray_on()
                    self.numMaxRamps += 1
                else:
                    break
        # IF HERE 5
        tearDown()
        self.Log.append_to_log(self.records)


            
