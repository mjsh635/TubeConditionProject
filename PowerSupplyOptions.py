"""
contains classes to create Powersupply objects for the various types of power supplies
"""

class DF3411():
    # constants for all powersupplies of this model


    def __init__(self, address):
        self.name = DF3411
        self.address = address

    def send_command(self):
        pass

