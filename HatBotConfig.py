"""Config for Hat Bot.

HatBotConfig() allows saving and loading configuration options for HatBot.

Version 1.1
"""

# imports
import configparser
import os
import sys

# File path for the config file.
# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    myDir = os.path.dirname(sys.executable)
elif __file__:
    myDir = os.path.dirname(__file__)


class HatBotConfig():
    """Class used for loading and saving options for Hat Bot."""

    # Sets the path of the config file, and the config object from import configparser
    # Settings Section
    SECTION_SETTINGS = "SETTINGS"
    OPTION_AUTOSTART = "autostart"
    DIR_FILES = "Directory Files"
    DIR_STREAM_SOURCES = "Stream sources"
    PATH_ICON_HAT = "path icons"
    # Sections
    # CREDENTIALS
    SECTION_CREDENTIALS = "CREDENTIALS"
    OPTION_CHANNEL_NAME = "streaming channel name"
    OPTION_BOT_USERNAME = "bot username"
    OPTION_OAUTH_TOKEN = "oauth token"

    # Character Request Commands
    SECTION_CHARACTER_REQUEST_COMMANDS = "Character Requests Commands"
    COMMAND_CHARACTER_REQUEST = "mod request character command"
    COMMAND_CHARACTER_REMOVE = "mod remove character command"
    COMMAND_CHARACTER_REPLACE = "mod replace character command"
    COMMAND_CHARACTER_INSERT = "mod insert character command"
    COMMAND_CHARACTER_CLEAR = "mod clear character list command"
    COMMAND_CHARACTER_LIST = "user show request list command"
    COMMAND_CHARACTER_HOW_TO_REQUEST = "user how to request command"

    # Character Requests Extended
    SECTION_CHARACTER_REQUESTS_EXTENDED = "Character Requests Extended"
    CHARACTER_TYPE = "character type"  # For example "God", "Survivor", "Killer"
    CHARACTER_RESPONSE_HOW_TO_REQUEST = "how to request response"
    CHARACTER_RESPONSE_NO_NEXT = "no character request next text"
    CHARACTER_RESPONSE_NO_LIST = "no character list text"
    # The image formats can be: "gif/png/jpg" etc... Should be listed
    # from highest priority to lowest priority and separated by '/'
    CHARACTER_IMAGE_FORMATS = "character image formats"
    PATH_CHARACTER_LIST_JSON = "path character list json"
    PATH_CHARACTER_LIST_TXT = "path character list text"
    PATH_CHARACTER_NEXT_TXT = "path character next text"
    # THE FOLLOWING DOES NOT INCLUDE THE IMAGE EXTENSION! MUst be added when called based on CHARACTER_IMAGE_FORMATS
    PATH_CHARACTER_NEXT_IMAGE = "path character next image source"
    DIR_CHARACTER_IMAGES = "Directory Character Images"
    # DOES NOT INCLUDE IMAGE EXTENSION!
    PATH_CHARACTER_BLANK_IMAGE_SOURCE = "path character blank image source"

    # Smite Api Section
    SECTION_SMITE_API = "SMITE API"
    SMITE_API_DEV_ID = "dev id"
    SMITE_API_AUTH_KEY = "auth key"
    SMITE_API_PC_URL = "pc url"
    SMITE_API_SESSION_ID = "session id"
    SMITE_API_SESSION_DATETIME = "datetime session created"
    SMITE_USERNAME = "smite username"
    COMMAND_DUEL_RANK = "duel rank command"
    COMMAND_CURRENT_SKIN = "current skin command"
    COMMAND_TIME_PLAYED = "time played command"
    COMMAND_WORSHIPPERS = "worshippers command"

    # FEATURES
    SECTION_TOGGLED_FEATURES = "Enabled and Disabled Features"
    FEATURE_CHARACTER_REQUEST = "feature character requests"
    FEATURE_SMITE_API = "feature smite api"
    FEATURE_SMITE_PORTRAIT = "feature smite portrait"
    FEATURE_SNAP = "feature snap"

    def __init__(self):
        self.config = configparser.ConfigParser()
        # Initialize the path to the configFile as None
        self.path_configFile = os.path.join(myDir, "HatBotConfig.ini")  # Default config path. Cannot be changed.
        # Set the path to the configFile based on what is in the config file. If there's not a config file, it will make a new one
        if (not os.path.exists(self.path_configFile)):
            print("Config file does not exist in: ", self.path_configFile, "\nCreating new config file..")
            self.CreateNewConfigFile()

    # Create a new SmiteAPIConfig.ini
    def CreateNewConfigFile(self):
        """Create a new config file."""
        if (not os.path.exists(self.path_configFile)):
            self.WriteToConfigFile()

        # Settings
        self.saveOption(self.SECTION_SETTINGS, self.OPTION_AUTOSTART, "0")
        self.saveOption(self.SECTION_SETTINGS, self.DIR_FILES, os.path.join(myDir, "files"))
        self.saveOption(self.SECTION_SETTINGS, self.DIR_STREAM_SOURCES, os.path.join(myDir, "stream sources"))
        self.saveOption(self.SECTION_SETTINGS, self.PATH_ICON_HAT, os.path.join(self.loadOption(
            self.SECTION_SETTINGS, self.DIR_FILES), "hat.png"))

        # Credentials
        self.saveOption(self.SECTION_CREDENTIALS, self.OPTION_BOT_USERNAME, "")
        self.saveOption(self.SECTION_CREDENTIALS, self.OPTION_CHANNEL_NAME, "")
        self.saveOption(self.SECTION_CREDENTIALS, self.OPTION_OAUTH_TOKEN, "")

        # Character Request Commands
        self.saveOption(self.SECTION_CHARACTER_REQUEST_COMMANDS, self.COMMAND_CHARACTER_REQUEST, "!req")
        self.saveOption(self.SECTION_CHARACTER_REQUEST_COMMANDS, self.COMMAND_CHARACTER_REMOVE, "!remove")
        self.saveOption(self.SECTION_CHARACTER_REQUEST_COMMANDS, self.COMMAND_CHARACTER_REPLACE, "!replace")
        self.saveOption(self.SECTION_CHARACTER_REQUEST_COMMANDS, self.COMMAND_CHARACTER_REPLACE, "!replace")
        self.saveOption(self.SECTION_CHARACTER_REQUEST_COMMANDS, self.COMMAND_CHARACTER_INSERT, "!insert")
        self.saveOption(self.SECTION_CHARACTER_REQUEST_COMMANDS, self.COMMAND_CHARACTER_CLEAR, "!clear")
        self.saveOption(self.SECTION_CHARACTER_REQUEST_COMMANDS, self.COMMAND_CHARACTER_LIST, "!list")
        self.saveOption(self.SECTION_CHARACTER_REQUEST_COMMANDS, self.COMMAND_CHARACTER_HOW_TO_REQUEST, "!request")

        # Character Requests Extended
        self.saveOption(self.SECTION_CHARACTER_REQUESTS_EXTENDED, self.CHARACTER_TYPE, "character")
        noCharacterNextText = "!request"
        self.saveOption(self.SECTION_CHARACTER_REQUESTS_EXTENDED, self.CHARACTER_RESPONSE_HOW_TO_REQUEST, "Streamer will play a request for...")
        self.saveOption(self.SECTION_CHARACTER_REQUESTS_EXTENDED, self.CHARACTER_RESPONSE_NO_NEXT, noCharacterNextText)
        self.saveOption(self.SECTION_CHARACTER_REQUESTS_EXTENDED, self.CHARACTER_RESPONSE_NO_LIST,
                        "There are no current characters requests. Type !request to learn how to request.")
        imageFormats = "gif/png/jpg"
        self.saveOption(self.SECTION_CHARACTER_REQUESTS_EXTENDED, self.CHARACTER_IMAGE_FORMATS, imageFormats)
        self.saveOption(self.SECTION_CHARACTER_REQUESTS_EXTENDED, self.PATH_CHARACTER_LIST_JSON, os.path.join(myDir, "files", "characterList.json"))
        self.saveOption(self.SECTION_CHARACTER_REQUESTS_EXTENDED, self.PATH_CHARACTER_LIST_TXT, os.path.join(myDir, "stream sources", "character list.txt"))
        self.saveOption(self.SECTION_CHARACTER_REQUESTS_EXTENDED, self.PATH_CHARACTER_NEXT_TXT, os.path.join(myDir, "stream sources", "character next.txt"))
        # DOES NOT INCLUDE IMAGE EXTENSION!
        self.saveOption(self.SECTION_CHARACTER_REQUESTS_EXTENDED, self.PATH_CHARACTER_NEXT_IMAGE, os.path.join(myDir, "stream sources", "Next Character Image"))
        # DOES NOT INCLUDE IMAGE EXTENSION!
        self.saveOption(self.SECTION_CHARACTER_REQUESTS_EXTENDED, self.PATH_CHARACTER_BLANK_IMAGE_SOURCE, os.path.join(myDir, "files", "blank image"))
        self.saveOption(self.SECTION_CHARACTER_REQUESTS_EXTENDED, self.DIR_CHARACTER_IMAGES, os.path.join(myDir, "Character Images"))

        self.initialize_config_smite_api()
        # Enabled/Disabled Features
        self.saveOption(self.SECTION_TOGGLED_FEATURES, self.FEATURE_CHARACTER_REQUEST, "1")
        self.saveOption(self.SECTION_TOGGLED_FEATURES, self.FEATURE_SMITE_API, "1")
        self.saveOption(self.SECTION_TOGGLED_FEATURES, self.FEATURE_SMITE_PORTRAIT, "1")
        self.saveOption(self.SECTION_TOGGLED_FEATURES, self.FEATURE_SNAP, "0")

        self.WriteToConfigFile()

    def initialize_config_smite_api(self):
        """Initialize default values for Smite API config settings."""
        # by using load_option with the default values, it will only save if the setting does not already exist.
        self.load_option(self.SECTION_SMITE_API, self.SMITE_API_DEV_ID, "")
        self.load_option(self.SECTION_SMITE_API, self.SMITE_API_AUTH_KEY, "")
        self.load_option(self.SECTION_SMITE_API, self.SMITE_API_PC_URL, "https://api.smitegame.com/smiteapi.svc")
        self.load_option(self.SECTION_SMITE_API, self.SMITE_API_SESSION_ID, "")
        self.load_option(self.SECTION_SMITE_API, self.SMITE_API_SESSION_DATETIME, "")

        self.load_option(self.SECTION_SMITE_API, self.COMMAND_TIME_PLAYED, "!timeplayed")
        self.load_option(self.SECTION_SMITE_API, self.COMMAND_DUEL_RANK, "!duelrank")
        self.load_option(self.SECTION_SMITE_API, self.COMMAND_WORSHIPPERS, "!worshippers")
        self.load_option(self.SECTION_SMITE_API, self.COMMAND_CURRENT_SKIN, "!skin")


    def WriteToConfigFile(self):
        #Whether the function was successful to writing to the config file or not.
        result = None
        try:
            with open(self.path_configFile, 'w') as configFile:
                self.config.write(configFile)
            result = True
        except Exception as e:
            print("Error: HatBotConfig.WriteToConfigFile() in path: ", self.path_configFile)
            print(e)
            result = False
        return result

    #Used for reading an option from the config file
    #section is the section name in the ini file
    #option is the option name in the ini file
    def loadOption(self, section, option):
        value = None
        if (self.path_configFile == None):
            return value
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

        #If the option is empty, it might as well be None
        if value == "":
            value = None

        return value

    def load_option(self, section, option, default=None):
        value = default
        if (self.path_configFile == None):
            return value
        self.config.read(self.path_configFile)

        if (self.config.has_section(section)):
            #The section exists..
            if (self.config.has_option(section, option)):
                value = self.config[section][option]
            else:
                print("No option named \"", option, "\" inside of section \"", section, "\" within \"", self.path_configFile, "\"."
                      "\n\tCheck ini file.", sep="")
                if default is not None:
                    self.saveOption(section, option, default)
        else:
            print("No section named \"", section, "\" within \"", self.path_configFile, "\".",
                  "\n\tCheck ini file.", sep="")
            if default is not None:
                self.saveOption(section, option, default)

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
            self.config[section] = {option: value}

        self.WriteToConfigFile()

    def loadBoolean(self, section, option):
        #Can be 0, 1, or None
        boolString = self.loadOption(section, option)
        if (boolString == None):
            boolString = "0"
        isTrue = bool(int(boolString))

        return isTrue


if __name__ == "__main__":
    print("Running HatBotConfig.py as main method...")
    config = HatBotConfig()
    config.initialize_config_smite_api()