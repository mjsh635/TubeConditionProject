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
                OpenedLogFile.writelines(log_data + "\n")                OpenedLogFile.writelines(f"{log_data}\n")

    def search_directory(self):
        """ Search path and return list of files 
        
        :returns: (list) returns list of files in constructors directory
        """
        files_in_dir = []

        # r=>root, d=>directories, f=>files
        for r, d, f in os.walk(self.folder_path):
            for item in f:
                if '.txt' in item:
                    files_in_dir.append(os.path.join(r, item))
        return files_in_dir

    def zip_files(self, foldername, files):
        """take all files return a zip'd folder containing them
        
        :param files: (list) files to be zipped
        
        :param foldername: (str) name of zip'd folder
        """
        with ZipFile((f"{self.folder_path}\\{foldername}.zip"), 'w') as zip:
            for txtfile in files:
                zip.write(txtfile)
        return f"{self.folder_path}\\{foldername}.zip"

