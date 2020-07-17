import sys, platform, socket, signal, math, time
from contextlib import contextmanager
import _thread

class DXM_Supply:

    def __init__(self, IP_address='192.168.1.4', port=50001):
        self.address = (
         IP_address, port)
        self.connect()
        self.remote_mode()
        raw_model = self.read_model_type()
        self.model = raw_model[1]
        self.disconnect()
        

    def is_emitting(self):
        resp = self.read_status_signals()
        print("emitting")
        if int(resp[1]) == 1:
            bool_is_emitting = True
        else:
            bool_is_emitting = False 
        return bool_is_emitting
    def is_ArcPresent(self):
        """Poll the supply and see if an Arc is present
        """
        faults = self.request_faults()
        if int(faults[1]) == 1:
            print("arc detected")
            return True
        else:
            return False        
    def xray_on(self):
        return self.__send_command(98, 1)

    def xray_off(self):
        return self.__send_command(98, 0)

    def reset_faults(self):
        return self.__send_command(31, '')

    def read_voltage_out(self):
        response = self.__send_command(19, '')
        if self.model == 'X4087':
            scaled_voltage = float(response[1]) * 0.00976
        elif self.model == 'X3481':
            scaled_voltage = float(response[1]) * 0.007326007
        elif self.model == 'X4911':
            scaled_voltage = float(response[1]) * 0.00976
        elif self.model == 'X4313':
            scaled_voltage = float(response[1]) * 0.007326007
        return scaled_voltage

    def read_model_type(self):
        return self.__send_command(26, '')

    def read_current_out(self):
        response = self.__send_command(19, '')
        if self.model == 'X4087':
            scaled_current = float(response[2]) * 0.007326
        elif self.model == 'X3481':
            scaled_current = float(response[2]) * 0.002442002
        elif self.model == 'X4911':
            scaled_current = float(response[2]) * 0.00366300
        elif self.model == 'X4313':
            scaled_current = float(response[2]) * 0.00488400
        return scaled_current

    def read_filament_current_out(self):
        response = self.__send_command(19, '')
      #  if self.model == 1200:
        scaled_fil = float(response[3]) * 0.001221
        return scaled_fil

    def request_voltage_set(self):
        response = self.__send_command(14, '')
        if self.model == 'X4087':
            scaled_voltage = float(response[1]) * 0.00976
        elif self.model == 'X3481':
            scaled_voltage = float(response[1]) * 0.007326007
        elif self.model == 'X4911':
            scaled_voltage = float(response[1]) * 0.00976
        elif self.model == 'X4313':
            scaled_voltage = float(response[1]) * 0.007326007
        return scaled_voltage

    def request_current_set(self):
        response = self.__send_command(15, '')
        if self.model == 'X4087':
            scaled_current = float(response[2]) * 0.007326
        elif self.model == 'X3481':
            scaled_current = float(response[2]) * 0.002442002
        elif self.model == 'X4911':
            scaled_current = float(response[2]) * 0.00366300
        elif self.model == 'X4313':
            scaled_current = float(response[2]) * 0.00488400
        return scaled_current

    def request_filament_limit_set(self):
        response = self.__send_command(16, '')
        #if self.model == 1200:
        scaled_fil = float(response[1]) * 0.001221
        return scaled_fil

    def request_Pre_Heat_set(self):
        response = self.__send_command(17, '')
        #if self.model == 1200:
        scaled_fil = float(response[1]) * 0.0006105
        return scaled_fil

    def set_voltage(self, voltage_to_set):
        """
        :param voltage_to_set: (float) 0-40
        """
        if self.model == 'X4087':
            raw_voltage_to_set = math.trunc(float(voltage_to_set) / 0.00976)
        elif self.model == 'X3481':
            raw_voltage_to_set = math.trunc(float(voltage_to_set) / 0.007326007)
        elif self.model == 'X4911':
            raw_voltage_to_set = math.trunc(float(voltage_to_set) / 0.00976)
        elif self.model == 'X4313':
            raw_voltage_to_set = math.trunc(float(voltage_to_set) / 0.007326007)
        return self.__send_command(10, raw_voltage_to_set)

    def set_current(self, current_to_set):
        """
        :param current_to_set: (float) 0-30
        """
        if self.model == 'X4087':
            raw_current_to_set = math.trunc(float(current_to_set) / .007326)
        elif self.model == 'X3481':
            raw_current_to_set = math.trunc(float(current_to_set) / 0.002442002)
        elif self.model == 'X4911':
            raw_current_to_set = math.trunc(float(current_to_set) / 0.00366300)
        elif self.model == 'X4313':
            raw_current_to_set = math.trunc(float(current_to_set) / 0.00488400)

        return self.__send_command(11, raw_current_to_set)

    def set_filament_limit(self, fil_limit_to_set):
        """
        :param fil_limit_to_set: (float) 0-5
        """
        raw_fil_limit_to_set = math.trunc(float(fil_limit_to_set) / 0.001221)
        return self.__send_command(12, raw_fil_limit_to_set)

    def set_filament_preheat(self, fil_preheat_to_set):
        """
        :param fil_preheat_to_set: (float) 0-2.5
        """
        
        raw_fil_preheat_to_set = math.trunc(float(fil_preheat_to_set) / 0.0006105)
        return self.__send_command(13, raw_fil_preheat_to_set)

    def local_mode(self):
        """ Switch the supply to local mode
        """
        return self.__send_command(99, 0)

    def remote_mode(self):
        """ Switch the supply to remote mode
        """
        return self.__send_command(99, 1)

    def request_faults(self):
        """return args of faults
        ARG1 = ARC
        ARG2 = Over Temperature
        ARG3 = Over Voltage
        ARG4 = Under Voltage
        ARG5 = Over Current
        ARG6 = Under Current
        """
        return self.__send_command(68, '')

    def read_status_signals(self):
        """
        <ARG1>  1 = HvOn, 0 = HvOff
        <ARG2>  1 = Interlock 1 Open, 0 = Interlock 1 Closed
        <ARG3>  1 = Fault Condition, 0 = No Fault
        <ARG4>  1 = Remote Mode, 0 = Local Mode"""
        return self.__send_command(22, '')

    def read_interlock_status(self):
        return self.__send_command(55, '')

    def __enter__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.address)

    def __exit__(self, e_type, e_val, e_traceback):
        self.socket.close()

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Attempting to connect...')
        self.socket.connect(self.address)

    def disconnect(self):
        self.socket.close()

    def __send_command(self, cmd, argm=''):
        """
        :param cmd: 2 ASCII characters representing the command ID

        :param *argm: Command Argument
        """
        argm = str(argm)
        if argm != '':
            self.argm = argm + ','
        else:
            self.argm = argm
        try:
            mes = '\x02{0},{1}\x03'.format(str(cmd), self.argm).encode('ascii')
            self.socket.send(mes)
            time.sleep(0.1)
            response = self.socket.recv(1024).decode('ascii')
            split_resp = response.split(sep=',')
            return split_resp

        except Exception as e:
            try:
                print(e)
            finally:
                e = None
                del e