#SmiteAPIConfig.py
#Contains all config information for SmiteAPIConfig.ini

#imports
import configparser
import os
import sys

#File path for the config file.
# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    myDir = os.path.dirname(sys.executable)
elif __file__:
    myDir = os.path.dirname(__file__)
PATH_CONFIGFILE = os.path.join(myDir, "SmiteAPIConfig.ini")

class SmiteAPIConfig(object):
    path_configFile = PATH_CONFIGFILE
    
    #Sections
    #API SETTINGS
    SECTION_API_SETTINGS = "API SETTINGS"
    OPTION_DEV_ID = "DEV_ID"
    OPTION_AUTH_KEY = "AUTH_KEY"
    OPTION_PC_URL = "PC_URL"
    OPTION_XBOX_URL = "XBOX_URL"
    OPTION_PLAYSTATION_URL = "PLAYSTATION_URL"
    
    #Session. Stores current session details so a new one doesn't need to be created everytime a request is called
    SECTION_SESSION = "SESSION"
    OPTION_SESSION_ID = "SESSION_ID"
    OPTION_SESSION_TIMESTAMP = "SESSION_TIMESTAMP"
    
    
    def __init__(self):
        #Sets the path of the config file, and the config object from import configparser
        self.config = configparser.ConfigParser()
        if (not os.path.exists(self.path_configFile)):
            print(self.path_configFile, "does not exist, creating a new one which will need to be updated..")
            self.CreateNewConfigFile()
    
    #Create a new SmiteAPIConfig.ini
    def CreateNewConfigFile(self):
        self.saveDevId("{DEV ID}")
        self.saveAuthKey("{AUTH KEY}")
        self.savePcUrl("https://api.smitegame.com/smiteapi.svc")
        self.saveXboxUrl("https://api.xbox.smitegame.com/smiteapi.svc")
        self.savePlayStationUrl("https://api.ps4.smitegame.com/smiteapi.svc")

        self.WriteToConfigFile()

           
    def WriteToConfigFile(self):
        #Whether the function was successful to writing to the config file or not.
        result = False
        try:
            with open(PATH_CONFIGFILE, 'w') as configFile:
                self.config.write(configFile)
            result = True
        except Exception as e:
            print("Error when writing to ", PATH_CONFIGFILE)
            print(e)
            result = False
        return result
    
    #Used for reading an option from the config file
    #section is the section name in the ini file
    #option is the option name in the ini file
    def loadOption(self, section, option):
        value = None
        self.config.read(self.path_configFile)
        
        if (self.config.has_section(section)):
            #The section exists..
            if (self.config.has_option(section, option)):
                value = self.config[section][option]
            else:
                print("No option named \"", option, "\" inside of section \"", section, "\" within \"", self.path_configFile, "\"."
                      "\n\tCheck ini file.", sep="")
        else:
            print("No section named \"", section, "\" within \"", self.path_configFile, "\".",
                  "\n\tCheck ini file.", sep="")

        if value == "":
            value = None
            
        return value
    
    def saveOption(self, section, option, value):
        if (value == None):
            value = ""
        else:
            value = str(value)
        
        self.config.read(self.path_configFile)
        if (self.config.has_section(section)):
            self.config[section][option] = value
        else:
            self.config[section] = {option : value}
            
        self.WriteToConfigFile()
        
    def loadDevId(self):
        return self.loadOption(self.SECTION_API_SETTINGS, self.OPTION_DEV_ID)
    
    def saveDevId(self, devId):
        self.saveOption(self.SECTION_API_SETTINGS, self.OPTION_DEV_ID, devId)
        
    def loadAuthKey(self):
        return self.loadOption(self.SECTION_API_SETTINGS, self.OPTION_AUTH_KEY)
        
        
    def saveAuthKey(self, authKey):
        self.saveOption(self.SECTION_API_SETTINGS, self.OPTION_AUTH_KEY, authKey)
        
    def loadPcUrl(self):
        return self.loadOption(self.SECTION_API_SETTINGS, self.OPTION_PC_URL)
    
    def savePcUrl(self, pcUrl):
        self.saveOption(self.SECTION_API_SETTINGS, self.OPTION_PC_URL, pcUrl)
    
    def loadXboxUrl(self):
        return self.loadOption(self.SECTION_API_SETTINGS, self.OPTION_XBOX_URL)
    
    def saveXboxUrl(self, xboxUrl):
        self.saveOption(self.SECTION_API_SETTINGS, self.OPTION_XBOX_URL, xboxUrl)
    
    def loadPlayStationUrl(self):
        return self.loadOption(self.SECTION_API_SETTINGS, self.OPTION_PLAYSTATION_URL)
    
    def savePlayStationUrl(self, playStationUrl):
        self.saveOption(self.SECTION_API_SETTINGS, self.OPTION_PLAYSTATION_URL, playStationUrl)

    def loadSessionId(self):
        return self.loadOption(self.SECTION_SESSION, self.OPTION_SESSION_ID)
        
    def saveSessionId(self, sessionId):
        self.saveOption(self.SECTION_SESSION, self.OPTION_SESSION_ID, sessionId)
    
    def loadSessionTimeStamp(self):
        return self.loadOption(self.SECTION_SESSION, self.OPTION_SESSION_TIMESTAMP)
    
    def saveSessionTimeStamp(self, sessionTimeStamp):
        self.saveOption(self.SECTION_SESSION, self.OPTION_SESSION_TIMESTAMP, sessionTimeStamp)
    
    
if __name__ == "__main__":
    print("Running SmiteAPIConfig.py as main method...")
    smiteConfig = SmiteAPIConfig()
    #ONLY FOR HATMASTER
    smiteConfig.saveDevId(3351)
    smiteConfig.saveAuthKey("19BDEE17CE094121A8EFE358658864B1")
    print(smiteConfig.loadAuthKey())
    #smiteConfig.setDevId(500)
    #print(smiteConfig.getDevId())
    
    
