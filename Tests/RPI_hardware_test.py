"""
This file should only be run on the RPI as it requires imports that 
are RPI libraries

Second, ensure that it is not connected to a system
"""

import unittest
import pathlib
import sys
PARENT_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(PARENT_DIR))
from MyScripts import Raspberry_PI_IO_Controller
import RPi.GPIO as io 
import board
import busio
i2c = busio.I2C(board.SCL, board.SDA)
rpi = Raspberry_PI_IO_Controller.RPIO(io,i2c,test_hardware=True)


class Test_Hardware(unittest.TestCase):
    def test_DAC(self):
        self.assertEqual(rpi.set_analog_out(1,1),"set")

    def test_ADC(self):
        self.assertGreaterEqual(rpi.read_analog_KV(),"read")
        self.assertGreaterEqual(rpi.read_analog_MA(),"read")

    def test_DI(self):
        self.assertEqual(rpi.readinput(),"read")

    def test_DO(self):
        self.assertEqual(rpi.set_GPIO(17,1),"set")
        self.assertEqual(rpi.set_GPIO(18,1),"set")

    def test_kvma_read(self):
        self.assertLessEqual(rpi.currentKVMA(),[1,1])

