import io
import os
from zipfile import ZipFile



class Conditioning_Logger():
    """ This class sets up the folders and files for logging, simply requiring
    that append_to_log() be called and passed data to be appended to file that is
    created by logfile_creation(). The zip_folder function can also be called to create a
    zip folder containing all the log files
    """

    def __init__(self, folder_path):
        """ Construct a logger and give it a location for its files

        :param folder: (str) folder path for file dir
        """
        self.folder_path = folder_path 
        self.file_name = "MissingSerialNumbers"

    def logfile_creation(self, file_name = "MissingSerialNumber"):
        """ Create a file if file does not exist
        
        :param file_name: (str) name for the file
        """
        if file_name == None:
            self.file_name = "MissingSerialNumbers"
        else:
            self.file_name = file_name

        if os.path.exists(f"{self.folder_path}\\{self.file_name}.txt"):
            return
        else:
            with open(f"{self.folder_path}\\{self.file_name}.txt", mode="w+"):
                pass

    def append_to_log(self, log_data):
        """ Append to the end of the file

        :param log_data: (str) data to be appeneded to the end of log file created
        by logfile_creation()
        """
        with open(f"{self.folder_path}\\{self.file_name}.txt", mode="a") as OpenedLogFile:
            if OpenedLogFile.writable():
                OpenedLogFile.writelines(f"{log_data}\n")


    def zip_files(self, foldername):
        """take all files return a zip'd folder containing them
        
        :param files: (list) files to be zipped
        
        :param foldername: (str) name of zip'd folder
        """
        with ZipFile((f"{self.folder_path}\\{foldername}.zip"), 'w') as zip:
            rootdir = os.path.basename(self.folder_path)
            for r, d, f in os.walk(self.folder_path):
                for item in f:
                    if '.txt' in item:
                        print(item)
                        filepath = os.path.join(r, item)
                        print(filepath)
                        parentpath = os.path.relpath(filepath, self.folder_path)
                        print(parentpath)
                        arcname = os.path.join(rootdir,parentpath)
                        print(arcname)
                        zip.write(filepath, arcname)
   
        return f"{self.folder_path}\\{foldername}.zip"

