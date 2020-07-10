import sys, pathlib
import unittest

PARENT_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(PARENT_DIR))
from MyScripts.DXM_300 import DXM300

class Test_responses(unittest.TestCase):

    def setUp(self):
        self.d = DXM300()
        self.d.connect()

    def tearDown(self):
        self.d.disconnect()

    def test_read_status(self):
        self.assertTrue(self.d.read_status_signals(),[22,0,0,0,0])

    def test_read_voltage(self):
        self.assertTrue(self.d.read_voltage_out(),[19,0,0,0,0])

    def test_read_current(self):
        self.assertTrue(self.d.read_current_out(),[19,0,0,0,0])
        
    def test_read_filament(self):
        self.assertTrue(self.d.read_filament_current_out(),[19,0,0,0,0])

