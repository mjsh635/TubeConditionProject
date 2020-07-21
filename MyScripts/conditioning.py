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
        self.currentReadKV = 0.0
        self.currentReadMA = 0.0
        self.currentReadFilcur = 0.0
        
        

    def start_cycle(self):
        # Start the cycle
        self.kill_sig.clear()
        self.cond_thread = threading.Thread(target=self.__conditioning)
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
        
    def __updateKVMA(self):
        resp = self.HV.read_volt_curr_filCur()
        self.currentReadKV = resp[0]
        self.currentReadMA = resp[1]
        self.currentReadFilcur = resp[2]
        return [self.currentReadKV, self.currentReadMA, self.currentReadFilcur]
    def __whileRamping(self):
        while self.HV.read_voltage_out() < (self.currentKVset * 0.90):
            self.__updateKVMA()
            time.sleep(0.33)
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
                        "maxMA" : 0.0 ,
                        "totalArcCount" : 0    
                        }
        """
    
        
        def setup():
            # set Filament Current Limit and Log it
            self.Log.append_to_log(f"""[Conditiong Mode, Starting Conditioning Cycle ||{datetime.datetime.today()}] \n""")
            self.HV.set_filament_limit(float(self.settings["filCurLim"]))
            self.Log.append_to_log((f"""[Conditiong Mode, Filament Current Limit: {self.settings["filCurLim"]}||{datetime.datetime.today()}]\n"""))

            # set Filament Preheat and log it
            self.HV.set_filament_preheat(float(self.settings["filPreHeat"]))
            self.Log.append_to_log((f"""[Conditiong Mode, Filament Preheat Set  : {self.settings["filPreHeat"]} ||{datetime.datetime.today()}]\n"""))    
            self.start_time = datetime.datetime.today()
            self.records["startDate"] = datetime.date.today()
            self.CondStarted = True
            self.condStepCount = float(self.settings["condStepCount"])
            self.condKVTarget = float(self.settings["condKVTarget"])
            self.condKVStart = float(self.settings["condKVStart"])
            self.condMATarget = float(self.settings["condMATarget"])
            self.condMAStart = float(self.settings["condMAStart"])
            self.condPostArcDwell = float(self.settings["condPostArcDwell"])
            self.condOffDwell = float(self.settings["condOffDwell"])
            self.kvStepSize = (float(self.condKVTarget) - float(self.condKVStart))/self.condStepCount
            self.maStepSize = (float(self.condMATarget) - float(self.condMAStart))/self.condStepCount
            self.condStepDwell = float(self.settings["condStepDwell"])
            self.condAtMaxDwell = float(self.settings["condAtMaxDwell"])
            self.maxKVReached = 0.0
            self.maxMAReached = 0.0
            self.kvTimeAtMax = 0.0
            self.maTimeAtMax = 0.0
            self.numMaxRamps = 0
            self.avgFilCur = 0.0
            self.filCurPoles = 0
            self.currentKVset = float(self.settings["condKVStart"])
            self.currentMAset = float(self.settings["condMAStart"])
            self.currentMAsetArced = float(self.currentMAset)
            self.currentKVsetArced = float(self.currentKVset)
            self.currentStepNumber = 0
            self.totalArcCount = 0
            self.runKVLoop = True
            self.arcCount = 0
            self.maxArcCount = 5

        def tearDown():
            self.CondStarted = False
        
            time.sleep(1)
            self.HV.xray_off()
            self.end_time = datetime.datetime.today()
            self.records["totalCondTime"] = (self.end_time - self.start_time)
            self.records["endDate"] = datetime.date.today()
            self.records["tubeSNum"] = self.settings["tubeSNum"]
            self.records["supplyModel"] = self.HV.model
            self.records["maxLvlsReached"] = [self.maxKVReached, self.maxMAReached]
            self.records["timeAtMax"] = [self.kvTimeAtMax, self.maTimeAtMax]
            self.records["numMaxRamps"] = self.numMaxRamps
            self.records["avgFilCur"] = self.avgFilCur
            self.records["totalArcCount"] = self.totalArcCount

       
             

        setup()
        print("started")
        
        while not self.kill_sig.is_set():
            # Conditioning Algo here
            while not self.kill_sig.is_set():
                #kv ramping loop with arc detection
                if (self.currentKVset < self.condKVTarget + self.kvStepSize):
                    self.HV.set_voltage(self.currentKVset)
                    self.Log.append_to_log(f"""[Conditioning Mode, voltage set to : {self.currentKVset},  ||{datetime.datetime.today()}]\n""")

                    self.HV.set_current(self.currentMAset)
                    self.Log.append_to_log(f"""[Conditioning Mode, Current set to : {self.currentMAset},  ||{datetime.datetime.today()}]\n""")
                    
                    if not self.HV.is_emitting():
                        self.Log.append_to_log(f"""[Conditioning Mode, Xrays turned on,  ||{datetime.datetime.today()}]\n""")
                        if not self.HV.read_interlock_status():
                            self.Log.append_to_log(f"""[Conditioning Mode, Xrays turned off due to interlock, ending conditioning Routine,  ||{datetime.datetime.today()}]\n""") 
                            self.kill_sig.set()
                        else:
                            self.HV.xray_on()
                            self.Log.append_to_log(f"""[Conditioning Mode, HV Ramping  ||{datetime.datetime.today()}]\n""") 
                            self.__whileRamping()
                            self.Log.append_to_log(f"""[Conditioning Mode, HV Ramping Complete  ||{datetime.datetime.today()}]\n""")

                          
                    end_time_loop_1 = datetime.datetime.now()+datetime.timedelta(minutes=self.condStepDwell)
                    self.currentMAsetArced = self.currentMAset + 1
                    self.__whileRamping()
                    
                    
                    self.Log.append_to_log(f"""[Conditioning Mode, current step number : {self.currentStepNumber} ||{datetime.datetime.today()}]\n""")
                    self.currentStepNumber += 1

                    while ((datetime.datetime.now() < end_time_loop_1) and (not self.kill_sig.is_set())):
                        
                        print(self.__updateKVMA())
                        if self.HV.is_emitting():
                            if self.HV.is_ArcPresent():
                                self.Log.append_to_log(f"""[Conditioning Mode, Arc Detected: ||{datetime.datetime.today()}]\n""")
                                if (self.arcCount <= self.maxArcCount+1):
                                    self.currentMAsetArced += 1
                                    if self.currentStepNumber == 0:
                                        
                                        if not self.HV.is_emitting():
                                            self.Log.append_to_log(f"""[Conditioning Mode, Xrays found to be off: ||{datetime.datetime.today()}]\n""")
                                            self.Log.append_to_log(f"""[Conditioning Mode, Xrays turned on ||{datetime.datetime.today()}]\n""")
                                            self.HV.xray_on()
                                            self.Log.append_to_log(f"""[Conditioning Mode, HV Ramping  ||{datetime.datetime.today()}]\n""") 
                                            self.__whileRamping()
                                            self.Log.append_to_log(f"""[Conditioning Mode, HV Ramping Complete  ||{datetime.datetime.today()}]\n""")

                                            
                                        self.HV.set_current(self.currentMAsetArced)

                                        self.Log.append_to_log(f"""[Conditioning Mode, Current set to : {self.currentMAsetArced},  ||{datetime.datetime.today()}]\n""")                    
                                            
                                    else:
                                        if not self.HV.is_emitting():
                                            self.Log.append_to_log(f"""[Conditioning Mode, Xrays found to be off: ||{datetime.datetime.today()}]\n""")
                                            self.HV.xray_on()
                                            self.Log.append_to_log(f"""[Conditioning Mode, HV Ramping  ||{datetime.datetime.today()}]\n""") 
                                            self.__whileRamping()
                                            self.Log.append_to_log(f"""[Conditioning Mode, HV Ramping Complete  ||{datetime.datetime.today()}]\n""")

                                        self.HV.set_voltage(self.currentKVset - self.kvStepSize)
                                        self.HV.set_current(self.currentMAsetArced)
                                        self.Log.append_to_log(f"""[Conditioning Mode, voltage set to : {self.currentKVset - self.kvStepSize},  ||{datetime.datetime.today()}]\n""")

                                        self.Log.append_to_log(f"""[Conditioning Mode, Current set to : {self.currentMAsetArced},  ||{datetime.datetime.today()}]\n""")

                                        self.arcCount += 1

                                        self.Log.append_to_log(f"""[Conditioning Mode, Arc count : {self.arcCount},  ||{datetime.datetime.today()}]\n""")
                                        self.Log.append_to_log(f"""[Conditioning Mode, Starting Arc Dwell||{datetime.datetime.today()}]\n""")
                                        end_time_loop_1 = datetime.datetime.now()+datetime.timedelta(minutes=self.condPostArcDwell)
                                else:
                                    self.Log.append_to_log(f"""[Conditioning Mode, Ending Conditioning routine due to: Arc count exceeding Max allowable Arcs ||{datetime.datetime.today()}]\n""")
                                    self.kill_sig.set()                                    
                            else:
                                
                                if self.arcCount != 0:
                                    self.totalArcCount += self.arcCount
                                    self.Log.append_to_log(f"""[Conditiong Mode, Recovered ||{datetime.datetime.today()}]\n""")
                                    self.arcCount = 0
                                    self.currentMAset = self.currentMAsetArced - 1
                                
                                self.HV.set_current(self.currentMAset)
                                
                                time.sleep(1)
                        else:
                            self.Log.append_to_log(f"""[Conditiong Mode, Xrays found to be off: ||{datetime.datetime.today()}]\n""")
                            if not self.HV.read_interlock_status():
                                self.Log.append_to_log(f"""[Conditioning Mode, Xrays turned off due to interlock, ending conditioning Routine,  ||{datetime.datetime.today()}]\n""") 
                                self.kill_sig.set()
                            else:
                                self.HV.xray_on()
                                self.Log.append_to_log(f"""[Conditiong Mode, Xrays turned on ||{datetime.datetime.today()}]\n""")
                                self.Log.append_to_log(f"""[Conditiong Mode, HV Ramping  ||{datetime.datetime.today()}]\n""") 
                                self.__whileRamping()
                                self.Log.append_to_log(f"""[Conditiong Mode, HV Ramping Complete  ||{datetime.datetime.today()}]\n""")
                                time.sleep(0.5)
                            
                    #update maxs and step
                    self.maxKVReached = self.currentKVset
                    self.maxMAReached = self.currentKVset
                    
                    #set KV to next value
                    print("step number: ",self.currentStepNumber)
                    self.currentKVset += self.kvStepSize
                  
                    self.HV.set_voltage(self.currentKVset)

                else:
                    self.Log.append_to_log(f"""[Conditioning Mode, KV Ramp completed {datetime.datetime.today()}]\n""")
                    #you've reached 1 on the graph at this point
                    self.currentKVset = (self.currentKVset-self.kvStepSize) * 0.75
                    self.HV.set_voltage(self.currentKVset)
                    self.currentMAset = self.currentMAset + self.maStepSize
                    self.currentStepNumber = 0
                    break

            self.Log.append_to_log(f"""[Conditioning Mode, Starting MA Ramp Loop 75% max KV : {self.currentKVset} ||{datetime.datetime.today()}]\n""")   

            while not self.kill_sig.is_set():
                self.currentKVsetArced = self.currentKVset        
                if self.currentMAset < (self.condMATarget + self.maStepSize):
                    self.HV.set_current(self.currentMAset)
                    self.Log.append_to_log(f"""[Conditioning Mode, Current set to : {self.currentMAset},  ||{datetime.datetime.today()}]\n""")
                    end_time_loop_2 = (datetime.datetime.now()+datetime.timedelta(minutes=self.condStepDwell))
                    while ((datetime.datetime.now() < end_time_loop_2) and not self.kill_sig.is_set()) :
                        
                        print(self.__updateKVMA())
                        if self.HV.is_emitting():
                            if self.HV.is_ArcPresent():
                                self.Log.append_to_log(f"""[Conditioning Mode, Arc Detected: ||{datetime.datetime.today()}]\n""")
                                if (self.arcCount <= self.maxArcCount+1):
                                    self.currentKVsetArced -= self.kvStepSize
                                    
                                    if not self.HV.is_emitting():
                                        self.Log.append_to_log(f"""[Conditioning Mode, Xrays found to be off: ||{datetime.datetime.today()}]\n""")
                                        if not self.HV.read_interlock_status():
                                            self.Log.append_to_log(f"""[Conditioning Mode, Xrays turned off due to interlock, ending conditioning Routine,  ||{datetime.datetime.today()}]\n""") 
                                            self.kill_sig.set()
                                        else:
                                            self.Log.append_to_log(f"""[Conditioning Mode, Xrays turned on ||{datetime.datetime.today()}]\n""")
                                            self.HV.xray_on()
                                            self.Log.append_to_log(f"""[Conditioning Mode, HV Ramping  ||{datetime.datetime.today()}]\n""") 
                                            self.__whileRamping()
                                            self.Log.append_to_log(f"""[Conditioning Mode, HV Ramping Complete  ||{datetime.datetime.today()}]\n""")

                                    self.HV.set_voltage(self.currentKVsetArced)
                                    self.Log.append_to_log(f"""[Conditioning Mode, voltage set to : {self.currentKVsetArced}||{datetime.datetime.today()}]\n""")
                                    self.arcCount += 1
                                    self.Log.append_to_log(f"""[Conditioning Mode, Arc count : {self.arcCount},  ||{datetime.datetime.today()}]\n""")

                                    self.Log.append_to_log(f"""[Conditioning Mode, Starting Arc Dwell||{datetime.datetime.today()}]\n""")
                                    end_time_loop_2 = datetime.datetime.now()+datetime.timedelta(minutes=self.condPostArcDwell)
                                else:
                                    self.Log.append_to_log(f"""[Conditioning Mode, Ending Conditioning routine due to: Arc count exceeding Max allowable Arcs ||{datetime.datetime.today()}]\n""")
                                    self.kill_sig.set()                                    
                            else:
                                if self.arcCount != 0:
                                    self.totalArcCount += self.arcCount
                                    self.Log.append_to_log(f"""[Conditiong Mode, Recovered ||{datetime.datetime.today()}]\n""")
                                    self.arcCount = 0
                                
                                self.HV.set_voltage(self.currentKVset)
                                time.sleep(1)
                        else:
                            self.Log.append_to_log(f"""[Conditiong Mode, Xrays found to be off: ||{datetime.datetime.today()}]\n""")
                            self.HV.xray_on()
                            self.Log.append_to_log(f"""[Conditiong Mode, Xrays turned on ||{datetime.datetime.today()}]\n""")
                            self.Log.append_to_log(f"""[Conditiong Mode, HV Ramping  ||{datetime.datetime.today()}]\n""") 
                            self.__whileRamping()
                            self.Log.append_to_log(f"""[Conditiong Mode, HV Ramping Complete  ||{datetime.datetime.today()}]\n""")
                            time.sleep(0.5)
                    #update maxs and step
                    self.maxMAReached = self.currentMAset
                    self.currentStepNumber += 1
                    #set KV to next value
                    print("step number: ",self.currentStepNumber)
                    self.currentMAset += self.maStepSize
                else:
                    self.Log.append_to_log(f"""[Conditioning Mode, MA Ramp completed {datetime.datetime.today()}]\n""")
                    #you've reached 2 on the graph at this point
                    self.currentStepNumber = 0
                    break
            
            print("Starting Max MA KV Ramp to Max")
            while not self.kill_sig.is_set():
                #kv ramping loop with arc detection
                if (self.currentKVset < self.condKVTarget + self.kvStepSize):
                    end_time_loop_3 = datetime.datetime.now()+datetime.timedelta(minutes=self.condStepDwell)
                    self.currentMAsetArced = self.currentMAset
                    while ((datetime.datetime.now() < end_time_loop_3) and (not self.kill_sig.is_set())):
                        
                        print(self.__updateKVMA())
                        if self.HV.is_ArcPresent():
                            if (self.arcCount <= self.maxArcCount+1):
                                self.currentMAsetArced -= 1

                                if not self.HV.is_emitting():
                                    if not self.HV.read_interlock_status():
                                        self.Log.append_to_log(f"""[Conditioning Mode, Xrays turned off due to interlock, ending conditioning Routine,  ||{datetime.datetime.today()}]\n""") 
                                        self.kill_sig.set()
                                    else:
                                        self.HV.xray_on()
                                
                                self.HV.set_current(self.currentMAsetArced)
                                self.arcCount += 1
                                end_time_loop_3 = datetime.datetime.now()+datetime.timedelta(minutes=self.condPostArcDwell)
                            else:
                                self.kill_sig.set()                                    
                        else:
                            if self.arcCount != 0:
                                self.arcCount = 0
                                
                            self.HV.set_current(self.currentMAset)
                            time.sleep(1)
                    #update maxs and step
                    self.maxKVReached = self.currentKVset
                    self.currentStepNumber += 1
                    #set KV to next value
                    print("step number: ",self.currentStepNumber)
                    self.currentKVset += self.kvStepSize
                    
                    self.HV.set_voltage(self.currentKVset)

                else:
                    self.currentStepNumber = 0
                    break
            
            self.Log.append_to_log(f"""[Conditioning Mode, Starting On/Off Cycles : {self.currentStepNumber} ||{datetime.datetime.today()}]\n""")
            print("Starting max KV MA ONOFF Cycle")

            for loop in range (4):
                if not self.kill_sig.is_set():
                    print("xray on time")
                    end_time_loop_4 = datetime.datetime.now()+ datetime.timedelta(minutes=self.condAtMaxDwell)
                    while ((datetime.datetime.now() < end_time_loop_4) and not self.kill_sig.is_set()): 
                        
                        print(self.__updateKVMA())
                        # powered max dwell if here 3
                        if self.HV.is_ArcPresent():
                                pass
                                
                        else:

                            time.sleep(1)
                    
                    self.HV.xray_off()
                    print("xray off time")
                    end_time_loop_5 = datetime.datetime.now()+datetime.timedelta(minutes=self.condOffDwell)
                    while ((datetime.datetime.now() < end_time_loop_5) and not self.kill_sig.is_set()):
                        
                        print(self.__updateKVMA())
                        # powered off dwell if here 4
                        time.sleep(1)

                    self.HV.xray_on()
                    self.numMaxRamps += 1
                else:
                    break
        if self.kill_sig.is_set():
            self.Log.append_to_log(f"""[Conditiong Mode, Requested Condition Stop ||{datetime.datetime.today()}]""")
        # IF HERE 5
        tearDown()
        self.Log.append_to_log(self.records)


            
