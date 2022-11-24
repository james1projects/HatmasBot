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
PATH_CONFIG_FILE = os.path.join(myDir, "config.ini")

class Option():
    def __init__(self, section_name, option_name):
        self.section_name = section_name
        self.option_name = option_name
        self.value = value

        return self

class Config():
    path_config_file = PATH_CONFIG_FILE

    # Sections
    # API SETTINGS
    SECTION_SMITE_API_SETTINGS = "API SETTINGS"
    SMITE_DEV_ID = "DEV_ID"
    SMITE_AUTH_KEY = "AUTH_KEY"
    PC_URL = "PC_URL"
    XBOX_URL = "XBOX_URL"
    PLAYSTATION_URL = "PLAYSTATION_URL"

    # Session. Stores current session details so a new one doesn't need to be created everytime a request is called
    SECTION_SESSION = "SESSION"
    OPTION_SESSION_ID = "SESSION_ID"
    OPTION_SESSION_TIMESTAMP = "SESSION_TIMESTAMP"

    BLANK_STRING = " "

    def __init__(self):
        # Sets the path of the config file, and the config object from import configparser
        self.config = configparser.Config()
        if (not os.path.exists(self.path_config_file)):
            print("\nConfig File:", self.path_config_file, "does not exist, creating a new one.")
            self.create_config_file()

    def create_config_file(self):
        # self.save_dev_id("{DEV ID}")
        # self.save_auth_key("{AUTH KEY}")
        self.save_pc_url("https://api.smitegame.com/smiteapi.svc")
        self.save_xbox_url("https://api.xbox.smitegame.com/smiteapi.svc")
        self.save_playstation_url("https://api.ps4.smitegame.com/smiteapi.svc")

        self.save_config_file()


    def save_config_file(self):
        # Whether the function was successful to writing to the config file or not.
        result = False
        try:
            with open(self.path_config_file, 'w') as config_file:
                self.config.write(config_file)
            result = True
        except Exception as e:
            print("Unable to write to ", self.path_config_file)
            print(e)
            result = False
        return result

    def load_option(self, section_name, option_name):
        # None values are stored as " ".
        value = None
        self.config.read(self.path_config_file)
        if (self.config.has_section(section_name)):
            if (self.config.has_option(section_name, option_name)):
                value = self.config[section_name][option_name]
            else:
                print("No option named \"", option_name, "\" inside of section \"", section_name, "\" within \"", self.path_config_file, "\"."
                      "\n\tCheck ini file.", sep="")
        else:
            print("No section named \"", section_name, "\" within \"", self.path_config_file, "\".",
                  "\n\tCheck ini file.", sep="")

        if value == self.BLANK_STRING:
            value = None
        return value

    def save_option(self, section_name, option_name, value):
        if value is None:
            value = " "
        else:
            value = str(value)

        self.config.read(self.path_config_file)
        if (self.config.has_section(section_name)):
            self.config[section_name][option_name] = value
        else:
            self.config[section_name] = {option_name: value}

        self.save_config_file()

        return value

    def load_smite_api_option(self, option_name):
        value = None
        section_name = self.SECTION_SMITE_API_SETTINGS
        value = self.load_option(self, section_name, option_name)

        return value

    def save_smite_api_option(self, option_name, value):
        section_name = self.SECTION_SMITE_API_SETTINGS
        value = self.save_option(self, self.SECTION_SMITE_API_SETTINGS, option_name, value)

        return value

