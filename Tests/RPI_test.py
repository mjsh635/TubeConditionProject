"""
This will be the start of the unit testing file.
this will use the "unittest" python library

https://docs.python.org/3/library/unittest.html#module-unittest

"""
import unittest
import pathlib
import sys
PARENT_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(PARENT_DIR))
from MyScripts import Raspberry_PI_IO_Controller
rpi = Raspberry_PI_IO_Controller.RPIO_DF3HVPSU(test=True)


class Test_Xray_On(unittest.TestCase):

    def test_xrayOn_low(self):
        self.assertEqual(rpi.XrayOn(-1, -1), "Xray value outside of bounds (0-60kv,0-80ma)")

    def test_xrayOn_high(self):
        self.assertEqual(rpi.XrayOn(61, 81), "Xray value outside of bounds (0-60kv,0-80ma)")

    def test_xrayOn_valid_low(self):
        self.assertEqual(rpi.XrayOn(0, 0), "xray set complete")

    def test_xrayOn_valid(self):
        self.assertEqual(rpi.XrayOn(32, 44), "xray set complete")

    def test_xrayOn_valid_high(self):
        self.assertEqual(rpi.XrayOn(60, 48), "xray set complete")

    def test_xrayOn_format(self):
        self.assertEqual(rpi.XrayOn("1..", "1.."), "the format of your input was incorrect, could not be parsed, too many periods?")


class Test_other(unittest.TestCase):
    def test_updateSettingsFile(self):
        self.assertEqual(rpi.updateSettingsFile(1, 1, 1, 1, 1, 1, 1, 1), "Update unsucessful, missing settings file")

    def test_updateHV(self):
        self.assertEqual(rpi.updateHVSettings(1, 1, 1, 1, 1, 1, 1, 1), "Update unsucessful, missing settings file")


class Test_Xray_Off(unittest.TestCase):

    def test_Xray_Off(self):
        self.assertEqual(rpi.XrayOff(), "xray turned off")