import io, os


filepath = r"Z:\MiscWorkJunk\TubeCondition\LoggingFile.txt"

def append_to_log(log_data, file_path):
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
    with open(filepath, mode="a+") as OpenedLogFile:
        if OpenedLogFile.writable():
            OpenedLogFile.writelines(log_data + "\n")
def create_log_file(folder_location):
    """
    Create a new log file in location, if the location already contains a
    log file, if log file already exists, this operation does nothing
    params:
    file_path (string):
        path of the log file location
    returns:
        nothing
    """
    pass
