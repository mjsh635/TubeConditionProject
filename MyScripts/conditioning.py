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
        self.condComplete = False
        self.HV = HVSupply
        self.settings = HVSettings
        self.Log = Logger
        self.kill_sig = threading.Event()
        self.currentReadKV = 0.0
        self.currentReadMA = 0.0
        self.currentReadFilcur = 0.0
        self.VoltageOverTime = {}
        self.CurrentOverTime = {}
        self.FilamentOverTime = {}
        
        

    def start_cycle(self):
        # Start the cycle
        self.kill_sig.clear()
        self.cond_thread = threading.Thread(target=self.__conditioning)
        self.cond_thread.start()

    def stop_cycle(self):
        # Set the kill_sig to end the conditioning routine
        self.kill_sig.set()

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
        def setup():
           ##### # when at max, every X seconds poll the fil current, and the 
           ##### # fil_Cur_To_Avg = []
           ##### # for poll in fil_Cur_To_Avg:
           ##### #     avgFilCur += poll
           ##### # avgFilCur / fil_Cur_To_Avg.count()

            #totalCondTime = currentTime + (condStepSize * 2) + (4 *(dwellOntime + dwellofftime))
            

            self.condComplete = False
            self.VoltageOverTime.clear()
            self.CurrentOverTime.clear()
            self.FilamentOverTime.clear()
            # set Filament Current Limit and Log it
            self.Log.append_to_log(f"""\n****************************************************\n""")
            self.Log.append_to_log(f"""Conditiong Mode, Starting Conditioning Cycle] \n""")
            self.HV.set_filament_limit(float(self.settings["filCurLim"]))
            self.Log.append_to_log((f"""Conditiong Mode, Filament Current Limit: {self.settings["filCurLim"]}]\n"""))

            # set Filament Preheat and log it
            self.HV.set_filament_preheat(float(self.settings["filPreHeat"]))
            self.Log.append_to_log((f"""Conditiong Mode, Filament Preheat Set  : {self.settings["filPreHeat"]}]\n"""))    
            self.start_time = str(datetime.date.today())
            self.records["startDate"] = datetime.date.today()
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
            time.sleep(1)
            self.HV.xray_off()
            self.condComplete = True
            self.end_time = datetime.datetime.today()
            self.records["totalCondTime"] = str((self.end_time - self.start_time))
            self.records["endDate"] = str(datetime.date.today())
            self.records["tubeSNum"] = self.settings["tubeSNum"]
            self.records["supplyModel"] = self.HV.model
            self.records["maxLvlsReached"] = [self.maxKVReached, self.maxMAReached]
            self.records["timeAtMax"] = [self.kvTimeAtMax, self.maTimeAtMax]
            self.records["numMaxRamps"] = self.numMaxRamps
            self.records["avgFilCur"] = self.avgFilCur
            self.records["totalArcCount"] = self.totalArcCount
            self.currentReadKV = 0
            self.currentReadMA = 0
            self.currentReadFilcur = 0


       
             

        setup()
        
        print("started")
        while not self.kill_sig.is_set():
            # KV Ramp up loop
            if (self.currentKVset < self.condKVTarget + self.kvStepSize):
            # keep ramping until the kv is at target
                self.HV.set_voltage(self.currentKVset)
                self.Log.append_to_log(f"""Conditioning Mode, voltage set to : {self.currentKVset}]\n""")
                # Set and log KV
                self.HV.set_current(self.currentMAset)
                self.Log.append_to_log(f"""Conditioning Mode, Current set to : {self.currentMAset},]\n""")
                # Set and log MA

                self._check_emitting()
                
                        

                # since Xrays are on, and havent hit KV Target, set dwell time delta
                # ##self.currentMAsetArced = self.currentMAset + 1
                self.__whileRamping()
                
                # log the current step number
                self.Log.append_to_log(f"""Conditioning Mode, current step number : {self.currentStepNumber}]\n""")
                self.currentStepNumber += 1

                self._increment_voltage()
                
                
                if self.arcCount != 0:
                    # there has been an arc at some point
                    # keep a total arc count and log the recovery
                    self.totalArcCount += self.arcCount
                    # reset the arc count
                    self.arcCount = 0
                    self.currentMAset = self.currentMAsetArced - 1        

                #update maxs and step
                self.maxKVReached = self.currentKVset
                self.maxMAReached = self.currentKVset
                
                #set KV to next value
                print("step number: ",self.currentStepNumber)
                self.currentKVset += self.kvStepSize

                self.HV.set_voltage(self.currentKVset)

            else:
                #if issue with over shooting target?
                self.currentKVset -= self.kvStepSize

                # the KV has hit its target
                #log the completion
                self.Log.append_to_log(f"""Conditioning Mode, KV Ramp completed]\n""")
                # set the KV to 75% of its total for the MA ramp
                self.currentKVset = self.currentKVset * 0.75
                self.HV.set_voltage(self.currentKVset)
                # start the MA Ramp
                self.currentMAset = self.currentMAset + self.maStepSize
                # reset the current step number
                self.currentStepNumber = 0
                # break out of the KV Ramp loop
                break
        # log the starting of the MA Ramp loop
        self.Log.append_to_log(f"""Conditioning Mode, Starting MA Ramp with 75% max KV : {self.currentKVset}]\n""")   

        while not self.kill_sig.is_set():
            # 75% KV, MA Ramp up Loop
            self.currentKVsetArced = self.currentKVset        
            if self.currentMAset < (self.condMATarget + self.maStepSize):
                # keep ramping untill MA is at target
                self.HV.set_current(self.currentMAset)
                self.Log.append_to_log(f"""Conditioning Mode, Current set to : {self.currentMAset}]\n""")
                # set and log the current
                
                self._check_emitting()

                # since Xrays are on, and havent hit MA Target, set dwell time delta        
                

                self.__whileRamping()
                
                # log the current step number
                self.Log.append_to_log(f"""Conditioning Mode, current step number : {self.currentStepNumber}]\n""")
                self.currentStepNumber += 1

                self._increment_Current()
                #update maxs and step
                self.maxMAReached = self.currentMAset
                
                #set KV to next value
                print("step number: ",self.currentStepNumber)
                self.currentMAset += self.maStepSize

                if self.arcCount != 0:
                    # there has been an arc at some point
                    # keep a total arc count and log the recovery
                    self.totalArcCount += self.arcCount
                    # reset the arc count
                    self.arcCount = 0
            else:
                
                #if issue with over shooting target?
                self.currentMAset -= self.maStepSize # can remove to have 1 step higher than target
                # the MA has hit its target
                self.Log.append_to_log(f"""Conditioning Mode, MA Ramp completed]\n""")
                # reset the step number
                self.currentStepNumber = 0
                # break out of the MA loop
                break
        
        self.Log.append_to_log(f"""Conditioning Mode, starting KV ramp with max MA : {self.currentKVset}]\n""")

        print("Starting Max MA KV Ramp to Max")
        while not self.kill_sig.is_set():
            #MA Max, KV 75% to max Ramp
            if (self.currentKVset < self.condKVTarget + self.kvStepSize):
                # keep ramping untill KV is back at target
                self._check_emitting()
                
                # since Xrays are on, and havent hit MA Target, set dwell time delta 
                
                # log and count current step number
                self.Log.append_to_log(f"""Conditioning Mode, current step number : {self.currentStepNumber}]\n""")
                self.currentStepNumber += 1

                self.currentMAsetArced = self.currentMAset

                self._kv_Reramp()

                if self.arcCount != 0:
                    # there has been an arc at some point
                    # keep a total arc count and log the recovery
                    self.totalArcCount += self.arcCount
                    # reset the arc count
                    self.arcCount = 0

                #update maxs and step
                self.maxKVReached = self.currentKVset
                
                #set KV to next value
                print("step number: ",self.currentStepNumber)
                self.currentKVset += self.kvStepSize
                
                self.HV.set_voltage(self.currentKVset)
                self.Log.append_to_log(f"""Conditioning Mode, voltage set to : {self.currentKVset}]\n""")

            else:
                self.currentKVset -= self.currentKVset # can remove to have 1 step higher than target
                # the MA has hit its target
                self.Log.append_to_log(f"""Conditioning Mode, Max MA, KV Ramp completed]\n""")
                # reset the step number
                self.currentStepNumber = 0
                # break out of the MA loop
                break
        
        self.Log.append_to_log(f"""Conditioning Mode, Starting On/Off Cycles : {self.currentStepNumber}]\n""")
        print("Starting max KV MA ONOFF Cycle")
        
        self._on_off_cycles()
        
        self.Log.append_to_log(f"""Conditioning Mode, On/Off Cycles Completed]\n""")
        print("Starting max KV MA ONOFF Cycle")

        if self.kill_sig.is_set():
            # received the kill signal, log that it ocurred
            self.Log.append_to_log(f"""Conditiong Mode, Requested Condition Stop]""")
        # start the tear down
        tearDown()
        # log the final report
        for item in self.records:
            self.Log.append_to_log(item)

        self.Log.append_to_log(f"""Conditiong Mode, Conditioning Complete]""")

    def _increment_voltage(self):
        end_time_loop_1 = datetime.datetime.now()+datetime.timedelta(minutes=self.condStepDwell)
        while ((datetime.datetime.now() < end_time_loop_1) and (not self.kill_sig.is_set())):
            # while loop until the current time is greater than the target endtime
            print(self.__updateKVMA())
            if self.HV.is_emitting():
                # is the xray still emitting?
                if self.HV.is_ArcPresent():
                    # is there an arc present? yes, so log and check conditions
                    self.Log.append_to_log(f"""Conditioning Mode, Arc Detected]\n""")
                    
                    if (self.arcCount <= self.maxArcCount+1):
                        # has there been more arcs than the allowed amount?
                        self.currentMAsetArced += 1
                        if self.currentStepNumber == 0:
                            # was this the first arc of the cycle?
                            
                            if not self.HV.is_emitting():
                                # was this arc big enough to knock out the xrays?
                                # restart the xrays and log everything
                                if not self.HV.read_interlock_status():
                                    # because the xrays were off due to an interlock, log and end the conditioning routine
                                    self.Log.append_to_log(f"""Conditioning Mode, Xrays turned off due to interlock, ending conditioning Routine]\n""") 
                                    self.kill_sig.set()

                                self.Log.append_to_log(f"""Conditioning Mode, Xrays found to be off]\n""")
                                self.Log.append_to_log(f"""Conditioning Mode, Xrays turned on]\n""")
                                self.HV.xray_on()
                                self.Log.append_to_log(f"""Conditioning Mode, HV Ramping]\n""") 
                                self.__whileRamping()
                                self.Log.append_to_log(f"""Conditioning Mode, HV Ramping Complete]\n""")
                                

                            # maintain the current settings and try and ride out the arcs and log 
                            self.HV.set_current(self.currentMAsetArced)
                            self.Log.append_to_log(f"""Conditioning Mode, Current set to : {self.currentMAsetArced}]\n""")                    
                                
                        else:
                            # this isnt the first cycle of the tube
                            if not self.HV.is_emitting():
                                # did the arc knock out the xrays?
                                # if so start the xrays again and log everything
                                if not self.HV.read_interlock_status():
                                    # because the xrays were off due to an interlock, log and end the conditioning routine
                                    self.Log.append_to_log(f"""Conditioning Mode, Xrays turned off due to interlock, ending conditioning Routine]\n""") 
                                    self.kill_sig.set()

                                self.Log.append_to_log(f"""Conditioning Mode, Xrays found to be off]\n""")
                                self.HV.xray_on()
                                self.Log.append_to_log(f"""Conditioning Mode, HV Ramping]\n""") 
                                self.__whileRamping()
                                self.Log.append_to_log(f"""Conditioning Mode, HV Ramping Complete]\n""")
                            # xrays were not knocked out, or they have been recovered
                            # set voltage back a step, and bump up the current
                            self.HV.set_voltage(self.currentKVset - self.kvStepSize)
                            self.HV.set_current(self.currentMAsetArced)
                            # log the voltage and current setpoint changes
                            self.Log.append_to_log(f"""Conditioning Mode, voltage set to : {self.currentKVset - self.kvStepSize}]\n""")
                            self.Log.append_to_log(f"""Conditioning Mode, Current set to : {self.currentMAsetArced}]\n""")
                            # increment the arc counter and log
                            self.arcCount += 1
                            self.Log.append_to_log(f"""Conditioning Mode, Arc count : {self.arcCount}]\n""")
                            # start the loop with a new end time equal to the post arc dwell value
                            self.Log.append_to_log(f"""Conditioning Mode, Starting Arc Dwell]\n""")
                            end_time_loop_1 = datetime.datetime.now()+datetime.timedelta(minutes=self.condPostArcDwell)
                    else:
                        # there has been more arcs than the allowed maximum, log and kill the conditioning routine
                        self.Log.append_to_log(f"""Conditioning Mode, Ending Conditioning routine due to: Arc count exceeding Max allowable Arcs]\n""")
                        self.kill_sig.set()                                    
                else:
                    

                    self.HV.set_current(self.currentMAset)  
                    time.sleep(1)
            else:
                # started the loop and xrays were off
                self.Log.append_to_log(f"""Conditiong Mode, Xrays found to be off(271)]\n""")
                if not self.HV.read_interlock_status():
                    # because the xrays were off due to an interlock, log and end the conditioning routine
                    self.Log.append_to_log(f"""Conditioning Mode, Xrays turned off due to interlock, ending conditioning Routine]\n""") 
                    self.kill_sig.set()
                else:
                    # the interlock is okay, so start up the xrays again and log everything
                    self.HV.xray_on()
                    self.Log.append_to_log(f"""Conditiong Mode, Xrays turned on]\n""")
                    self.Log.append_to_log(f"""Conditiong Mode, HV Ramping]\n""") 
                    self.__whileRamping()
                    self.Log.append_to_log(f"""Conditiong Mode, HV Ramping Complete]\n""")
                    time.sleep(0.5)
    
    def _increment_Current(self):
        end_time_loop_2 = (datetime.datetime.now()+datetime.timedelta(minutes=self.condStepDwell))
        while ((datetime.datetime.now() < end_time_loop_2) and not self.kill_sig.is_set()) :
        # while loop until the current time is greater than the target end time
            print(self.__updateKVMA())
            if self.HV.is_emitting():
                    # is the xray still emitting?
                if self.HV.is_ArcPresent():
                    # is there an arc present? yes, so log and check conditions
                    self.Log.append_to_log(f"""Conditioning Mode, Arc Detected]\n""")

                    if (self.arcCount <= self.maxArcCount+1):
                            # has there been more arcs than the allowed amount?
                        self.currentKVsetArced -= self.kvStepSize
                        # reduce the kv by 1 step and try again

                        if not self.HV.is_emitting():
                            # was this arc big enough to knock out the xrays?
                                # restart the xrays and log everything
                                
                            if not self.HV.read_interlock_status():
                                # because the xrays were off due to an interlock, log and end the conditioning routine
                                self.Log.append_to_log(f"""Conditioning Mode, Xrays turned off due to interlock, ending conditioning Routine]\n""") 
                                self.kill_sig.set()

                            # xrays were not knocked out, or they have been recovered
                                
                            self.Log.append_to_log(f"""Conditioning Mode, Xrays turned on]\n""")
                            self.HV.xray_on()
                            self.Log.append_to_log(f"""Conditioning Mode, HV Ramping]\n""") 
                            self.__whileRamping()
                            self.Log.append_to_log(f"""Conditioning Mode, HV Ramping Complete]\n""")
                        # set voltage back a step, 
                        self.HV.set_voltage(self.currentKVsetArced)
                        self.Log.append_to_log(f"""Conditioning Mode, voltage set to : {self.currentKVsetArced}]\n""")
                        # increment the arc counter and log
                        self.arcCount += 1
                        self.Log.append_to_log(f"""Conditioning Mode, Arc count : {self.arcCount}]\n""")
                        # start the loop with a new end time equal to the post arc dwell value
                        self.Log.append_to_log(f"""Conditioning Mode, Starting Arc Dwell]\n""")
                        end_time_loop_2 = datetime.datetime.now()+datetime.timedelta(minutes=self.condPostArcDwell)
                    else:
                        # there has been more arcs than the allowed maximum, log and kill the conditioning routine
                        self.Log.append_to_log(f"""Conditioning Mode, Ending Conditioning routine due to: Arc count exceeding Max allowable Arcs]\n""")
                        self.kill_sig.set()                                    
                else:
                    # no arc was detected 
                    self.HV.set_voltage(self.currentKVset)
                    time.sleep(1)
            else:
                # started the loop and xrays were off
                self.Log.append_to_log(f"""Conditiong Mode, Xrays found to be off]\n""")

                if not self.HV.read_interlock_status():
                    # because the xrays were off due to an interlock, log and end the conditioning routine
                    self.Log.append_to_log(f"""Conditioning Mode, Xrays turned off due to interlock, ending conditioning Routine]\n""") 
                    self.kill_sig.set()
                else:
                    # the interlock is okay, so start up the xrays again and log everything
                    self.HV.xray_on()
                    self.Log.append_to_log(f"""Conditiong Mode, Xrays turned on]\n""")
                    self.Log.append_to_log(f"""Conditiong Mode, HV Ramping]\n""") 
                    self.__whileRamping()
                    self.Log.append_to_log(f"""Conditiong Mode, HV Ramping Complete]\n""")
                    time.sleep(0.5)

    def _kv_Reramp(self):
        end_time_loop_3 = datetime.datetime.now()+datetime.timedelta(minutes=self.condStepDwell)
        while ((datetime.datetime.now() < end_time_loop_3) and (not self.kill_sig.is_set())):
            # while loop until the current time is greater than the target end time
            print(self.__updateKVMA())
            if self.HV.is_emitting():
                # is the xray still emitting?
                if self.HV.is_ArcPresent():
                        # is there an arc present? yes, so log and check conditions
                    self.Log.append_to_log(f"""Conditioning Mode, Arc Detected]\n""")

                    if (self.arcCount <= self.maxArcCount+1):
                        # has there been more arcs than the allowed amount?
                        self.currentMAsetArced -= 1
                        # reduce the MA by 1 step and try again

                        if not self.HV.is_emitting():
                            # was this arc big enough to knock out the xrays?
                                # restart the xrays and log everything

                            if not self.HV.read_interlock_status():
                                # because the xrays were off due to an interlock, log and end the conditioning routine
                                self.Log.append_to_log(f"""Conditioning Mode, Xrays turned off due to interlock, ending conditioning Routine,  ||{datetime.datetime.today()}]\n""") 
                                self.kill_sig.set()

                            # xrays were not knocked out, or they have been recovered    
                            self.Log.append_to_log(f"""Conditioning Mode, Xrays turned on]\n""")
                            self.HV.xray_on()
                            self.Log.append_to_log(f"""Conditioning Mode, HV Ramping]\n""") 
                            self.__whileRamping()
                            self.Log.append_to_log(f"""Conditioning Mode, HV Ramping Complete]\n""")    

                        # set current back a step,
                        self.HV.set_current(self.currentMAsetArced)
                        # increment the arc counter and log
                        self.arcCount += 1
                        self.Log.append_to_log(f"""Conditioning Mode, Arc count : {self.arcCount}]\n""")
                        # start the loop with a new end time equal to the post arc dwell value
                        self.Log.append_to_log(f"""Conditioning Mode, Starting Arc Dwell]\n""")
                        end_time_loop_3 = datetime.datetime.now()+datetime.timedelta(minutes=self.condPostArcDwell)
                    else:
                        # there has been more arcs than the allowed maximum, log and kill the conditioning routine
                        self.Log.append_to_log(f"""Conditioning Mode, Ending Conditioning routine due to: Arc count exceeding Max allowable Arcs]\n""")
                        self.kill_sig.set()                                    
                else:
                    # no arc was detected
                    if self.arcCount != 0:
                        # there has been an arc at some point
                        # keep a total arc count and log the recovery
                        self.totalArcCount += self.arcCount
                        self.Log.append_to_log(f"""[Conditiong Mode, Recovered]\n""")
                        # reset the arc count
                        self.arcCount = 0
                        
                    self.HV.set_current(self.currentMAset)
                    time.sleep(1)
            else:
                # started the loop and xrays were off
                self.Log.append_to_log(f"""Conditiong Mode, Xrays found to be off]\n""")

                if not self.HV.read_interlock_status():
                    # because the xrays were off due to an interlock, log and end the conditioning routine
                    self.Log.append_to_log(f"""Conditioning Mode, Xrays turned off due to interlock, ending conditioning Routine]\n""") 
                    self.kill_sig.set()
                else:
                    # the interlock is okay, so start up the xrays again and log everything
                    self.HV.xray_on()
                    self.Log.append_to_log(f"""Conditiong Mode, Xrays turned on]\n""")
                    self.Log.append_to_log(f"""Conditiong Mode, HV Ramping]\n""") 
                    self.__whileRamping()
                    self.Log.append_to_log(f"""Conditiong Mode, HV Ramping Complete]\n""")
                    time.sleep(0.5)

    def _on_off_cycles(self,cycle_count = 4):
        ### comments stop here as this all needs work
        ### things that needed added in this loop 
        ### count time at max
        ### poll for filament current and record in a list, also count number of polls
        # for loop in range (4):
        #     # Xray on off cycle
        #     if not self.kill_sig.is_set():
        #         print("xray on time")
        #         end_time_loop_4 = datetime.datetime.now()+ datetime.timedelta(minutes=self.condAtMaxDwell)
        #         while ((datetime.datetime.now() < end_time_loop_4) and not self.kill_sig.is_set()): 
                    
        #             print(self.__updateKVMA())
        #             # powered max dwell if here 3
        #             if self.HV.is_ArcPresent():
        #                     pass
                            
        #             else:

        #                 time.sleep(1)
                
        #         self.HV.xray_off()
        #         print("xray off time")
        #         end_time_loop_5 = datetime.datetime.now()+datetime.timedelta(minutes=self.condOffDwell)
        #         while ((datetime.datetime.now() < end_time_loop_5) and not self.kill_sig.is_set()):
                    
        #             print(self.__updateKVMA())
        #             # powered off dwell if here 4
        #             time.sleep(1)

        #         self.HV.xray_on()
        #         self.numMaxRamps += 1
        #     else:
        #         break
        #  # temp
        pass

    def _check_emitting(self):
        if not self.HV.is_emitting():
            # check if the xrays are off
            self.Log.append_to_log(f"""Conditioning Mode, Xrays turned on]\n""")
            # log if they are off
            if not self.HV.read_interlock_status():
                # check if they are off due to the interlocks
                self.Log.append_to_log(f"""Conditioning Mode, Xrays turned off due to interlock, ending conditioning Routine]\n""") 
                self.kill_sig.set()
                # since they are off because the interlock is open, kill the routine

            else:
                # since the interlocks aren't the reason for xray off
                # Xray on, wait for ramp complete, log operations
                self.HV.xray_on()
                self.Log.append_to_log(f"""Conditioning Mode, HV Ramping]\n""") 
                self.__whileRamping()
                self.Log.append_to_log(f"""Conditioning Mode, HV Ramping Complete]\n""")

    def _update_Graph_Values(self):
        self.VoltageOverTime.update()
        self.CurrentOverTime.update()
        self.FilamentOverTime.update()