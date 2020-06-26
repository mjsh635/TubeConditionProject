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

        with open(r"Z:\MiscWorkJunk\TubeCondition\static\Settings\settings.pkl","rb") as file:
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
        
    # import board
    # import busio
    # import adafruit_ads1x15.ads1015 as ADS
    # from adafruit_ads1x15.analog_in import AnalogIn

    # # Create the I2C bus
    # i2c = busio.I2C(board.SCL, board.SDA)
    # dev1_addres = 0x00
    # dev2_addres = 0x00
    # dev3_addres = 0x00
    # # Create the ADC object using the I2C bus
    # ADC_Device1 = ADS.ADS1015(i2c,dev1_addres)
    # # ADC_Device2 = ADS.ADS1015(i2c, dev2_addres)
    # # ADC_Device3 = ADS.ADS1015(i2c, dev3_addres)

    # Dev1chan0 = AnalogIn(ADC_Device1, ADS.P0)
    # Dev1chan1 = AnalogIn(ADC_Device1, ADS.P1)
    # Dev1chan2 = AnalogIn(ADC_Device1, ADS.P2)
    # Dev1chan3 = AnalogIn(ADC_Device1, ADS.P3)

    # # Dev2chan0 = AnalogIn(ADC_Device2, ADS.P0)
    # # Dev2chan1 = AnalogIn(ADC_Device2, ADS.P1)
    # # Dev2chan2 = AnalogIn(ADC_Device2, ADS.P2)
    # # Dev2chan3 = AnalogIn(ADC_Device2, ADS.P3)

    # # Dev3chan0 = AnalogIn(ADC_Device3, ADS.P0)
    # # Dev3chan1 = AnalogIn(ADC_Device3, ADS.P1)
    # # Dev3chan2 = AnalogIn(ADC_Device3, ADS.P2)
    # # Dev3chan3 = AnalogIn(ADC_Device3, ADS.P3)

    # def readValue( channel):
    #     channel_data = [channel.value, channel.voltage]
    #     return channel_data

    def set_GPIO(self,pin, value):
        pass

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
            with open(r"Z:\MiscWorkJunk\TubeCondition\static\Settings\settings.pkl","wb") as file:
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
    