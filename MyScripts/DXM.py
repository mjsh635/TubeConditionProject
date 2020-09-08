import sys, platform, socket, signal, math, time
from contextlib import contextmanager
import _thread


class DXM_Supply:

    def __init__(self, IP_address='192.168.1.4', port=50001):
        

        self.address = (
         IP_address, port)
        # # self.connect()
        # self.remote_mode()
        # raw_model = self.read_model_type()
        self.model = ""
        self.connected = False
        try:
            with self:
                self.read_model_type()
                self.connected = True
                print(f"{self.address} Connected as {self.model}")
        except socket.timeout as TOE:
            print(TOE, self.address)
            self.connected = False
        # # self.disconnect()
        

    def is_emitting(self):
        """
        :return: (bool) is the supply emitting"""
        with self:
            resp = self.read_status_signals()
            if int(resp[1]) == 1:
                bool_is_emitting = True
            else:
                bool_is_emitting = False 
            return bool_is_emitting

    def is_ArcPresent(self):
        """Poll the supply and see if an Arc is present
        :return: (bool) if the supply has an arc present
        """
        with self:
            faults = self.request_faults()
            if int(faults[1]) == 1:
                print("arc detected")
                return True
            else:
                return False  

    def xray_on(self):
        """ send command for xray_on
        :return: response from supply"""
        with self:
            return self.__send_command(98, 1)

    def xray_off(self):
        """ send command for xray_off
        :return: response from supply"""
        with self:
            return self.__send_command(98, 0)

    def reset_faults(self):
        """ send command to reset supply faults
        :return: response from supply"""
        with self:
            return self.__send_command(31, '')

    def read_voltage_out(self):
        """ send command to read voltage

        :return: (float) KV readout from supply"""
        with self:
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
        """ send command to read model number

        :return: (str) model number from supply"""
        self.remote_mode()
        with self:
            resp = self.__send_command(26, '')
            ans = resp[1]
            if (ans[0] == "D"): # this is to handle the fact spellman is stupid
                                # and decided to have some supplies with different Model styles
                if ans == "DXM02":
                    ans = "X3481"
                elif ans == "DXM20":
                    ans = "X4313"
                elif ans == "DXM21":
                    ans = "X4911"
                elif ans == "DXM33":
                    ans = "X4087"
            self.model = ans
            return ans

    def read_current_out(self):
        """ send command to read current

        :return: (float) MA readout from supply"""
        with self:
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
        """ send command to read filament current

        :return: (float) fil current readout from supply"""
        with self:
            response = self.__send_command(19, '')
      #  if self.model == 1200:
        scaled_fil = float(response[3]) * 0.001221
        return scaled_fil

    def read_volt_curr_filCur(self):
        with self:
            response = self.__send_command(19, '')
        if self.model == 'X4087':
            scaled_voltage = float(response[1]) * 0.00976 #40kv
            scaled_current = float(response[2]) * 0.007326 #30ma
        elif self.model == 'X3481':
            scaled_voltage = float(response[1]) * 0.007326007 #30kv
            scaled_current = float(response[2]) * 0.002442002 #10ma
        elif self.model == 'X4911':
            scaled_voltage = float(response[1]) * 0.00976 # 40kv
            scaled_current = float(response[2]) * 0.00366300 #15ma
        elif self.model == 'X4313':
            scaled_voltage = float(response[1]) * 0.007326007 #30KV
            scaled_current = float(response[2]) * 0.00488400 #20ma
        scaled_fil = float(response[3]) * 0.001221

        return [scaled_voltage, scaled_current, scaled_fil]

    def request_voltage_set(self):
        """ send command to read voltage setpoint

        :return: (float) KV readout from supply"""
        with self:
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
        """ send command to read current setpoint

        :return: (float) MA readout from supply"""
        with self:
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
        """ send command to read filament limit setpoint

        :return: (float) Filament current setpoint readout from supply"""
        with self:
            response = self.__send_command(16, '')
        #if self.model == 1200:
        scaled_fil = float(response[1]) * 0.001221
        return scaled_fil

    def request_Pre_Heat_set(self):
        """ send command to read filament preheat setpoint

        :return: (float) Filament preheat setpoint readout from supply"""
        with self:
            response = self.__send_command(17, '')
        #if self.model == 1200:
        scaled_fil = float(response[1]) * 0.0006105
        return scaled_fil

    def set_voltage(self, voltage_to_set):
        """ command to set voltage
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
        with self:
            return self.__send_command(10, raw_voltage_to_set)

    def set_current(self, current_to_set):
        """ Command to set current on supply
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
        with self:
            return self.__send_command(11, raw_current_to_set)

    def set_filament_limit(self, fil_limit_to_set):
        """ Command to set filament current on supply
        :param fil_limit_to_set: (float) 0-5
        """
        raw_fil_limit_to_set = math.trunc(float(fil_limit_to_set) / 0.001221)
        with self:
            return self.__send_command(12, raw_fil_limit_to_set)

    def set_filament_preheat(self, fil_preheat_to_set):
        """Command to set filament preheat on supply
        :param fil_preheat_to_set: (float) 0-2.5
        """
        
        raw_fil_preheat_to_set = math.trunc(float(fil_preheat_to_set) / 0.0006105)
        with self:
            return self.__send_command(13, raw_fil_preheat_to_set)

    def local_mode(self):
        """ Switch the supply to local mode
        """
        with self:
            return self.__send_command(99, 0)

    def remote_mode(self):
        """ Switch the supply to remote mode
        """
        with self:
            return self.__send_command(99, 1)
    
    def read_network_settings(self):
        """ read the network settings from the supply
        """
        with self:
            return self.__send_command(50, 1)

    def write_network_settings(self,device_name="DefaultSpellman", ip_addr='192.168.1.4',port=50001, subnet='255.0.0.0',gate_way="192.168.1.1", mac_default='00:40:9D:35:7C:B7'):
        """ Write new network settings to the supply
        """
        with self:
            arg = f"{device_name},{ip_addr},{port},{subnet},{gate_way},{mac_default}" 
            print(arg)
            return self.__send_command(51, arg)

    def request_faults(self):
        """return args of faults
        ARG1 = ARC
        ARG2 = Over Temperature
        ARG3 = Over Voltage
        ARG4 = Under Voltage
        ARG5 = Over Current
        ARG6 = Under Current
        """
        with self:
            return self.__send_command(68, '')

    def read_status_signals(self):
        """ Command to read status
        <ARG1>  1 = HvOn, 0 = HvOff
        <ARG2>  1 = Interlock 1 Open, 0 = Interlock 1 Closed
        <ARG3>  1 = Fault Condition, 0 = No Fault
        <ARG4>  1 = Remote Mode, 0 = Local Mode"""
        with self:
            return self.__send_command(22, '')

    def read_interlock_status(self):
        """Command to read interlock status on supply True = OK
        """
        with self:
            resp = self.__send_command(55, '')

        if resp[1] == '0':
            return True
        else:
            return False

    # @contextmanager
    # def _time_limit(self,time_length):
    #     if sys.platform.startswith("linux"):
    #         import signal
    #         def signal_handler(signum, frame):
    #             raise OSError("timed out! Could not connect to supply")
    #         signal.signal(signal.SIGALRM,signal_handler)
    #         signal.alarm(time_length)
    #         try:
    #             yield
    #         finally:
    #             signal.alarm(0)
    #     else:
    #         yield

    def __enter__(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect(self.address)
        except Exception as e:
            print(e ,self.address)
            raise socket.timeout

        

    def __exit__(self, e_type, e_val, e_traceback):
        self.socket.close()

    def try_connect(self):
        """Attempt connection with Powersupply"""
        try:
            with self:
                self.read_model_type()
                self.connected = True
        except socket.timeout as we:
            print(we,self.address)
            self.connected = False


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
            time.sleep(0.3)
            self.socket
            response = self.socket.recv(1024).decode('ascii')
            split_resp = response.split(sep=',')
            if split_resp != None:
                raise TypeError
            

        except Exception as e:
            try:
                print(e)
            finally:
                e = None
                del e
        except TypeError as t:
            print(e)
