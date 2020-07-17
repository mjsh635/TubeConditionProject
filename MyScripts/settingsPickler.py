import pickle
import sys,pathlib,os


class SettingsPickle():
    """this class handles the creation and reading/writing of
    the settings.pkl that contains all the import settings for
    the operation of the system
    """
    def __init__(self, path):
        self.path = path
        def settings_File_creation():
            """Local function to check if the file exist, if it
            does not it will create a new empty file in that location
            """
            if os.path.exists(self.path):
                #if exists, return
                return
            else:
                #if doesnt exist, open, write following settings
                with open(self.path, mode="wb+") as f:
                    self.settings = {
                        "currKV" : 0.0,
                        "currMA" : 0.0,
                        "tubeSNum" : "",
                        "tubeType" : "",
                        "filCurLim" : 0.0,
                        "filPreHeat" : 0.0,
                        "condKVStart" : 0.0,
                        "condKVTarget" : 0.0,
                        "condMAStart" : 0.0,
                        "condMATarget" : 0.0,
                        "condStepDwell" : 0.0,
                        "condAtMaxDwell" : 0.0,
                        "condPostArcDwell" : 0.0,
                        "condOffDwell" : 0.0,
                        "condStepCount" : 0.0,
                        "maxKV" : 0.0,
                        "maxMA" : 0.0,
                        "maxTubeMA" : 12,
                        "maxTubeKV" : 0.5    
                        }
                    # pickle the file 
                    pickle.dump(self.settings,f)
        # execute the local function on __init__
        settings_File_creation()

    def read_pickle(self):
        """ read the data contained in the pickle file
        :return: pickled object from file at self.path
        """
        with open(self.path, mode="rb+") as f:
            return pickle.load(f)

    def write_pickle(self, object_to_pickle):
        """ write the data back to the pickle file to 
        ensure the users settings are mantained
        :return: nothing
        """
        with open(self.path, mode= "wb+") as f:
            pickle.dump(object_to_pickle, f)