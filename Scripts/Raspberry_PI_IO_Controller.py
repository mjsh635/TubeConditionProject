import time
import pickle
class outside_bounds_exception(Exception):
    pass

class RPIO():
    def __init__(self):
        
        # settings = {
        #     "currKV" : 0.0,
        #     "currMA" : 0.0,
        #     "condKVStart" : 0.0,
        #     "condKVTarget" : 0.0,
        #     "condMAStart" :0.0,
        #     "condMATarget" : 0.0,
        #     "condStepDwell" : 0.0,
        #     "CondPostArcDwell" :0.0,
        #     "CondOffDwell" : 0.0,
        #     "CondStepCount" :   0.0,
        # }
        # with open(r"Z:\MiscWorkJunk\TubeCondition\static\Settings\settings.pkl","wb") as file:
        #     pickle.dump(settings,file)

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
    
    def set_GPIO(self,pin, value):
        self.io.output(pin,value)

    def set_analog_out(self, kv, ma):
        value_to_set1 = math.floor((kv*10.0*6.825))
        value_to_set2 = math.floor((ma*10.0*5.11875))
        self.dac1.raw_value = 2000#value_to_set1
        self.dac2.raw_value = 2000#value_to_set2
    
    def read_analog_KV(self):
        KVraw = self.adc.read_adc(0)
        self.readKV = KVraw/68.25

    def read_analog_MA(self):
        MAraw = self.adc.read_adc(1)
        self.readMA = MAraw/51.1875

    def readinput(self):
        print(self.io.input(22), self.io.input(27))

    def XrayOn(self,kv,mA):
        """set KV, set MA, check if xray already on, if is do nothing, if not turn on DO to turn on xray, wait 2 seconds, check that xrays turned on
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
            pass

        finally:
            return mes
        return mes

            
    def updateHVSettings(self,condKVStart,condKVTarget,condMAStart,condMATarget,condStepDwell,CondPostArcDwell,CondOffDwell,CondStepCount):
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
        print(self.read_analog_KV())
        print(self.read_analog_MA())
        mes = str("current kv: {0} and ma: {1}").format(self.read_analog_KV(),self.read_analog_MA())
        print(mes)
        return mes
    