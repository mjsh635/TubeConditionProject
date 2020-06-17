import time
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)
dev1_addres = 0x00
dev2_addres = 0x00
dev3_addres = 0x00
# Create the ADC object using the I2C bus
ADC_Device1 = ADS.ADS1015(i2c,dev1_addres)
ADC_Device2 = ADS.ADS1015(i2c, dev2_addres)
ADC_Device3 = ADS.ADS1015(i2c, dev3_addres)

Dev1chan0 = AnalogIn(ADC_Device1, ADS.P0)
Dev1chan1 = AnalogIn(ADC_Device1, ADS.P1)
Dev1chan2 = AnalogIn(ADC_Device1, ADS.P2)
Dev1chan3 = AnalogIn(ADC_Device1, ADS.P3)

Dev2chan0 = AnalogIn(ADC_Device2, ADS.P0)
Dev2chan1 = AnalogIn(ADC_Device2, ADS.P1)
Dev2chan2 = AnalogIn(ADC_Device2, ADS.P2)
Dev2chan3 = AnalogIn(ADC_Device2, ADS.P3)

Dev3chan0 = AnalogIn(ADC_Device3, ADS.P0)
Dev3chan1 = AnalogIn(ADC_Device3, ADS.P1)
Dev3chan2 = AnalogIn(ADC_Device3, ADS.P2)
Dev3chan3 = AnalogIn(ADC_Device3, ADS.P3)

def readValue(channel):
    channel_data = [channel.value,channel.voltage]
    return channel_data

def set_GPIO(pin, value):
    