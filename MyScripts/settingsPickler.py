import pickle
import sys,pathlib,os


class SettingsPickle():

    def __init__(self, path):
        self.path = path
        def settings_File_creation():
            if os.path.exists(self.path):
                return
            else:
                with open(self.path, mode="wb+") as f:
                    self.settings = {
                        "currKV" : 0.0,
                        "currMA" : 0.0,
                        "tubeSNum" : "",
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
                        "maxMA" : 0.0      
                        }
                    pickle.dump(self.settings,f)
        settings_File_creation()

    def read_pickle(self):
        with open(self.path, mode="rb+") as f:
            return pickle.load(f)

    def write_pickle(self, object_to_pickle):
        with open(self.path, mode= "wb+") as f:
            pickle.dump(object_to_pickle, f)