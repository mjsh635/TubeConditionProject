import math
from adafruit_bus_device import i2c_device

# Toggle last two bits to change address


class AD5671R:
    _AD5675_ADDRESS_ONE = 0b00001100
    _AD5675_ADDRESS_TWO = 0b00001101
    def __init__(self, i2c, *, address=_AD5675_ADDRESS_ONE):
        self._i2c = i2c_device.I2CDevice(i2c, address)
        self._address = address
        self._BUFFER = bytearray(3)

    def write_Val(self, val, channel):
        """
        :param val: (int 0-65535) Val to set on channel
        :param channel: (int 0-7) DAC channel
        """
        scaled_val = math.trunc(val / 0.00003814755)
        scaled_val &= 0xFFFF
        self._BUFFER[0] = 0b00110000 | channel 
        self._BUFFER[1] = scaled_val >> 8
        self._BUFFER[2] = scaled_val & 0xFF
        
        with self._i2c as i2c:
          print(self._BUFFER[0],self._BUFFER[1],self._BUFFER[2])  
          i2c.write(self._BUFFER)