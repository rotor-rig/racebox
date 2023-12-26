
import configparser

class RaceboxConfig:
    def __init__(self):
        self.rbCfFileName = 'rbconfig.ini'
        self.config = configparser.ConfigParser()
        self.config.read([self.rbCfFileName])
        self.__setDefaults()
        
    def __setDefaults(self):
        defaults = [
            ['Signals', 'defaultOn2Off', 0.75], #seconds -- hoot on-->off (length of hoot) for most signals
            ['Signals', 'finishOn2Off', 0.25], #seconds -- hoot on-->off (length of hoot) for finishes
            ['Signals', 'defaultSequence', 0], #the signal sequence selected by default in the interface
            ['Relays', 'serialRelayPort', '/dev/ttyUSB0'], # for Windows, this is probably COM1 (or COM2, COM3 etc)
            ['Files', 'finshFileUseDefaultFolder', True],
            ['Files', 'finishFileFolder', 'Documents'],
            ['Lights', 'defaultOn2Off', 0.75], #seconds -- light on-->off when light is flashing
            ['Lights', 'defaultSequence', 0] #the light sequence selected by default in the interface
        ]
        configUpdate = False
        for d in defaults:
            if not self.config.has_section(d[0]):
                self.config.add_section(d[0])
                configUpdate = True
            if not self.config.has_option(d[0],d[1]):
                self.config.set(d[0],d[1],str(d[2]))
                configUpdate = True
        if configUpdate:
            with open(self.rbCfFileName, 'w') as cf: self.config.write(cf)
    
    def get(self, section, key):
        return self.config.get(section, key)