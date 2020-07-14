import io
import os


class Conditioning_Logger():

    def __init__(self, path):
        """
        :param path: (str) if path doesnt exist, create the file
        """
        def logfile_creation():
            if os.path.exists(self.filepath):
                return
            else:
                with open(self.filepath, mode="w+") as f:
                    pass
        self.filepath = path
        logfile_creation()


    def append_to_log(self, log_data):
        """
        Open the log file, and then append the data to the end of the file,
        closing the file afterwards

        params:
        log_data (string):
            data to be appended on the end of the log file
        file_path (string):
            path of the log file
        returns:
            nothing
        """
        with open(self.filepath, mode="a") as OpenedLogFile:
            if OpenedLogFile.writable():
                OpenedLogFile.writelines(log_data + "\n")
