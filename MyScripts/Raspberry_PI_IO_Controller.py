"""This class is sorta a one off, it was designed with specific intention to handle the
analog communication with the DF3 highvoltage powersupply that does not support communication
over Ethernet
"""
import sys, path
PARENT_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(PARENT_DIR))
import time
import pickle
import math


class outside_bounds_exception(Exception):
    pass



class RPIO_DF3HVPSU():
    
    def __init__(self,io=None,i2c=None,test=False,test_hardware=False):
        self.test = test
        self.test_hardware = test_hardware

        if not self.test:
            import Adafruit_ADS1x15
            from MyScripts.DAC_Controller import AD5671R
            self.io = io
            io.setmode(io.BCM)
            self.adc = Adafruit_ADS1x15.ADS1115(address=0x48)  #0x48
            self.dac1 = AD5671R(i2c ,address=AD5671R._AD5675_ADDRESS_ONE) #0x62
            self.dac2 = AD5671R(i2c ,address=AD5671R._AD5675_ADDRESS_TWO)
            self.io.setup(17,io.OUT) # XRAY ON/OFF  
            self.io.setup(18,io.OUT) # RESET SUPPLY
            self.io.setup(22,io.IN,)  #XRAYS ARE ON
            self.io.setup(27,io.IN) #PSU IS FAULTED

            if not self.test_hardware:
                with open(r"/home/pi/Desktop/TubeConditionProject-Dev/static/Settings/settings.pkl","rb") as file:
                    settings = pickle.load(file)
                
                self.currKV = settings["currKV"]
                self.currMA = settings["currMA"]
                self.condKVStart = settings["condKVStart"]
                self.condKVTarget = settings["condKVTarget"]
                self.condMAStart = settings["condMAStart"]
                self.condMATarget = settings["condMATarget"]
                self.condStepDwell = settings["condStepDwell"]
                self.CondPostArcDwell = settings["CondPostArcDwell"]
                self.CondOffDwell = settings["CondOffDwell"]
                self.CondStepCount = settings["CondStepCount"]
                self.readKV = 0.0
                self.readMA = 0.0
                self.set_GPIO(17,1)
                self.set_GPIO(18,1)

        elif self.test:
            self.currKV = 1
            self.currMA = 2
            self.condKVStart = 3
            self.condKVTarget = 4
            self.condMAStart = 5
            self.condMATarget = 6
            self.condStepDwell = 7
            self.CondPostArcDwell = 8
            self.CondOffDwell = 9
            self.CondStepCount = 10
            self.readKV = 0.0
            self.readMA = 0.0
    
    def set_GPIO(self,pin, value):
        """
        :param pin: (int) pin to set

        :param value: (int) On/Off 1/0

        """
        if not self.test:
            self.io.output(pin,value)
            return "set"

    def set_analog_out(self, kv, ma):
        """
        :param kv: (float) 0 - 60 value for target KV

        :param ma: (float) 0 - 80 value for target MA
        """
        if not self.test:
            value_to_set1 = math.floor((kv*10.0*6.825))
            value_to_set2 = math.floor((ma*10.0*5.11875))
            self.dac1.raw_value = value_to_set1
            self.dac2.raw_value = value_to_set2
            return "set"
    
    def read_analog_KV(self):
        if not self.test:
            KVraw = self.adc.read_adc(0)
            self.readKV = KVraw/68.25
            return "read"

    def read_analog_MA(self):
        if not self.test:
            MAraw = self.adc.read_adc(1)
            self.readMA = MAraw/51.1875
            return "read"

    def readinput(self):
        if not self.test:
            print(self.io.input(22), self.io.input(27))
            return "read"
        

    def XrayOn(self,kv,mA):
        """set KV, set MA, check if xray already on, if is do nothing, if not turn on DO to turn on xray, wait 2 seconds, check that xrays turned on

        :param kv: (float) 0 - 60 value for target KV

        :param ma: (float) 0 - 80 value for target MA
        """
        mes = ""
        try:
            setKV = float(kv)
            setMA = float(mA)
            if ((setKV >= 0.0 and setKV <=60.0) and (setMA>=0.0 and setMA<=80.0)):
                self.currKV = setKV
                self.currMA = setMA
                self.set_analog_out(self.currKV,self.currMA)
                self.set_GPIO(17,0)
                time.sleep(0.5)
                self.set_GPIO(17,1)
                mes = "xray set complete"
            else:
                raise outside_bounds_exception

        except outside_bounds_exception:
            mes = "Xray value outside of bounds (0-60kv,0-80ma)"
        
        except ValueError:
            print("value error")
            mes = "the format of your input was incorrect, could not be parsed, too many periods?"
            
        finally:
            print (mes)
            return mes

    def XrayOff(self):
        """turn off the DO to xray, check feedback that xray is off
        """
        print("Xrays turning off")
        self.set_GPIO(17,1)

        mes = "xray turned off"
        return mes 

    def updateSettingsFile(self,condKVStart,condKVTarget,condMAStart,condMATarget,condStepDwell,CondPostArcDwell,CondOffDwell,CondStepCount):
        """
        :param condKVStart: (float)
        :param condKVTarget: (float)
        :param condMAStart: (float)
        :param condMATarget: (float)
        :param condStepDwell: (float)
        :param CondPostArcDwell: (float)
        :param CondOffDwell: (float)
        :param CondStepCount: (float)
        """
        mes = ""
        print("test")
        settings = {
            "currKV" : 0.0,
            "currMA" : 0.0,
            "condKVStart" : condKVStart,
            "condKVTarget" : condKVTarget,
            "condMAStart" : condMAStart,
            "condMATarget" : condMATarget,
            "condStepDwell" : condStepDwell,
            "CondPostArcDwell" : CondPostArcDwell,
            "CondOffDwell" : CondOffDwell,
            "CondStepCount" : CondStepCount      
        }
        try:
            with open(r"/home/pi/Desktop/TubeConditionProject-Dev/static/Settings/settings.pkl","wb") as file:
                pickle.dump(settings, file)
            mes = "Updated Sucessfully"

        except:
            mes = "Update unsucessful, missing settings file"

        finally:
            return mes
        return mes

            
    def updateHVSettings(self,condKVStart,condKVTarget,condMAStart,condMATarget,condStepDwell,CondPostArcDwell,CondOffDwell,CondStepCount):
        """
        :param condKVStart: (float)
        :param condKVTarget: (float)
        :param condMAStart: (float)
        :param condMATarget: (float)
        :param condStepDwell: (float)
        :param CondPostArcDwell: (float)
        :param CondOffDwell: (float)
        :param CondStepCount: (float)
        """
        self.condKVStart = condKVStart
        self.condKVTarget = condKVTarget
        self.condMAStart = condMAStart
        self.condMATarget = condMATarget
        self.condStepDwell = condStepDwell
        self.CondPostArcDwell = CondPostArcDwell
        self.CondOffDwell = CondOffDwell
        self.CondStepCount = CondStepCount

        mes = self.updateSettingsFile(condKVStart,condKVTarget,condMAStart,condMATarget,condStepDwell,CondPostArcDwell,CondOffDwell,CondStepCount)

        
        return mes
    
    def currentKVMA(self):
        if not self.test:
            if not self.test_hardware:
                self.read_analog_KV()
                self.read_analog_MA()
                mes = str("current kv: {0} and ma: {1}").format(self.readKV,self.readMA)
                print(mes)
            elif self.test_hardware:
                self.read_analog_KV()
                self.read_analog_MA()
                mes = [self.readKV, self.readMA]
        return mes
