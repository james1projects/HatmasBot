"""Twitch Bot Created by Hatmaster.

Has custom features for Character Requests,
Smite API commands, and more! Use class TwitchBot

Version 1.1
"""

# Imports
import Commands
import HatBotConfig
import os
import sys
import socket
import time

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    myDir = os.path.dirname(sys.executable)
elif __file__:
    myDir = os.path.dirname(__file__)

# Global Variables/Configuration
feature_snap = True

canSendMessages = True

class TwitchBot(object):
    """Twitch Bot Created by Hatmaster."""

    def __init__(self):
        config = HatBotConfig.HatBotConfig()
        self.connection_data = ("irc.chat.twitch.tv", 6667)
        self.oauth_token = config.loadOption(config.SECTION_CREDENTIALS, config.OPTION_OAUTH_TOKEN)
        self.bot_username = config.loadOption(config.SECTION_CREDENTIALS, config.OPTION_BOT_USERNAME)
        self.channel_name = "#" + config.loadOption(config.SECTION_CREDENTIALS, config.OPTION_CHANNEL_NAME).lower()
        self.consoleMessages = 0

        self.isLoggedIn = False
        self.isConnected = False
        self.server = socket.socket()
        self.stop = False

        self.debug_all_twitch_info = True

        if (self.isConnected == False):
            self.connectUntilSuccess()

        if (self.isConnected):
            self.server.send(bytes('PASS ' + self.oauth_token + '\r\n', 'utf-8'))
            self.server.send(bytes('NICK ' + self.bot_username + '\r\n', 'utf-8'))
            self.server.send(bytes('CAP REQ :twitch.tv/tags\r\n', 'utf-8'))
            self.server.send(bytes('JOIN ' + self.channel_name + '\r\n', 'utf-8'))

            self.log("Joining " + self.channel_name[1:] + "'s Channel...")
        else:
            self.log("Failed to connect, check internet connection or settings.")

    def connectUntilSuccess(self, MAX_ATTEMPTS=20):
        """Try connecting to twitch until the max attempts have been reached, or
        the connection is a success"""

        connectAttempts = 1
        while(self.isConnected == False):
            if (connectAttempts < MAX_ATTEMPTS):
                try:
                    self.server.connect(self.connection_data)
                    self.isConnected = True
                    print("Connected.")
                except:
                    # Connetion failed.
                    self.log("Connection failed... trying again...")
                    time.sleep(2**connectAttempts)
                    connectAttempts += 1

    # Send a message to the connected twitch channel via the twitch bot
    def sendMessage(self, message):
        global canSendMessages

        if (self.isConnected and canSendMessages):
            self.log(self.bot_username + " -> " + message)
            self.server.send(bytes('PRIVMSG ' + self.channel_name +
                                   ' :' + message + '\r\n', 'utf- 8'))

    def log(self, text):
        print(text, end='\n')

    def main(self):
        if (self.isConnected and self.stop == False):
            self.server.settimeout(.05)
            try:
                rawdata = (self.server.recv(2048))
            except:
                # There is no data from twitch currently.
                return
            try:
                data_string = rawdata.decode("utf-8")
            except UnicodeDecodeError as e:
                print("UnicodeDecodeError")
                print(e)
                return
            if (self.debug_all_twitch_info):
                print("twitch data:", data_string)

            if (":tmi.twitch.tv NOTICE * :Login authentication failed\r\n" in data_string):
                self.log("Error: Login authentication failed.\noauth token is incorrect or expired. Please click \"Get my oauth token\" in settings to generate a new one.")

            # Ping / Pong to stay connected to twitch.
            if (rawdata == bytes("PING :tmi.twitch.tv\r\n", 'utf-8')):
                self.server.send(bytes('PONG :tmi.twitch.tv\r\n', 'utf-8'))

            if (self.isLoggedIn == True):
                if (data_string != "" and "PRIVMSG" in data_string):
                    self.parseTags(data_string)

            if ("Welcome, GLHF!\r\n:tmi.twitch.tv" in data_string):
                self.isLoggedIn = True
                self.log("Successfully logged into " + self.channel_name[1:] + "'s chat!")

    def exitbot(self):
        self.server.send(bytes('PART ' + self.channel_name + '\r\n', 'utf-8'))
        self.isConnected = False
        self.stop = True
        del self

    def parse_twitch_message(self, twitch_message_data):
        tagStart = twitch_message_data.find("@")
        tagEnd = twitch_message_data.find("PRIVMSG")-1
        # Sometimes twitch_message_data starts with multiple new lines. We avoid that by
        # skipping to the first @
        twitch_message_data = twitch_message_data[tagStart:]

        chat_message = None
        tagStart += 1  # Do not include the '@'
        # There is a twitch irc tags data being sent, could contain a chat message
        tags_dict = {}
        tags = twitch_message_data[tagStart:tagEnd]
        tags_list = tags.split(";")
        for tag in tags_list:
            equal_location = tag.find("=")
            if (equal_location != -1):
                # There is an equals sign in the tag...
                tag_key = tag[:equal_location]
                tags_dict[tag_key] = tag[equal_location + 1:]

        priv_msg_string = str("PRIVMSG " + self.channel_name + " :")
        message_start = twitch_message_data.find(priv_msg_string)
        if (message_start != -1):
            message_start += len(priv_msg_string)  # Do not include the 'PRIVMSG #channelname :'
            # There is a chat message.
            chat_message = twitch_message_data[message_start:]
            tags_dict["chat_message"] = chat_message

            displayname = tags_dict.get('display-name', None)

            if (displayname != None and chat_message != None):
                # LOG CHAT MESSAGE, if console only just log it as regular text.
                list_colors_to_log = [tags_dict["color"], "#FFFFFF"]
                list_emotes = tags_dict['emotes'].split("/")

                self.log_twitch_message(displayname, chat_message, displayname_color=tags_dict["color"], list_emotes=list_emotes)
                #self.log(tags_dict["display-name"] + ": "+ chatMessage)
                self.checkCommand(tags_dict)
            else:
                print("SOMETHING WENT WRONG WITH DISPLAYNAME, CHATMESSAGE (", displayname, ", ", chat_message, ")", sep="")
                print("\t", twitch_message_data)

    def parseTags(self, data_string):
        tagStart = data_string.find("@")
        tagEnd = data_string.find("PRIVMSG")
        if (tagStart != -1 and tagEnd != -1):
            # Sometimes multiple messages are sent in twitch irc. Handle
            # Them by using recursion.
            newline_count = data_string.count("\n")

            for i in range(newline_count):
                twitch_message_data = data_string[tagStart:data_string.find("\n")+1]
                print("twitch_message_data:", twitch_message_data, end="--END\n")
                self.parse_twitch_message(twitch_message_data)
                data_string = data_string[data_string.find("\n")+1:]
                newline_count = data_string.count("\n")

    def log_twitch_message(self, displayname, message, displayname_color="#FFFFFF", list_emotes=None):
        """
        Parameters
        ----------
        displayname : String
            DESCRIPTION.
        message : String
            DESCRIPTION.
        displayname_color : String, optional
            DESCRIPTION. The default is color_text.
        list_emotes : list, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        """

        default_chat_message_color = "#FFFFFF"
        list_colors_to_log = [displayname_color]
        list_strings_to_log = [displayname, ": " + message]

        self.log_colored_message(list_strings_to_log, list_colors_to_log)

    def log_colored_message(self, list_strings, list_colors=None, list_emotes=None):
        """
        Parameters
        ----------
        list_strings : list
            List of strings in order to log to console
        list_colors : list, optional
            List of colors that belong to the strings to log to console
        list_emotes : list, optional
            list of emotes in the message
        Returns
        -------
        None.

        """
        # Override this function to actually include list_colors, for this object
        # is python console only which does not include colors.

        # LOG CHAT MESSAGE, if console only just log it as regular text.
        string_to_log = list_strings.pop(0)
        for string in list_strings:
            string_to_log += string

        self.log(string_to_log)

    def checkCommand(self, tags_dict):
        if ("chat_message" in tags_dict):
            #print("mod:", tags_dict['mod'], type(tags_dict['mod']), chatterPermission)
            chatMessage = tags_dict["chat_message"].rstrip("\n\r")
            params = chatMessage.split(" ")  # Split the message based on spaces
            command = params.pop(0).lower()  # Gets rid of the command name in params

            Commands.checkCommand(self, command, tags_dict, params)


def validate_token():
    valid = True
    config = HatBotConfig.HatBotConfig()
    oauth_token = config.loadOption(config.SECTION_CREDENTIALS, config.OPTION_OAUTH_TOKEN)
    if(oauth_token == None or not (oauth_token.startswith("oauth:"))):
        valid = False

    return valid


if __name__ == "__main__":
    if (validate_token()):
        oBot = TwitchBot()
        while(True):
            oBot.main()
    else:
        print("invalid oauth token")
