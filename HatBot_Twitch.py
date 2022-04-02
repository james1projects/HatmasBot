"""Twitch Bot Created by Hatmaster.

Has custom features for Character Requests,
Smite API commands, and more! Use class TwitchBot.

Version 1.1
"""

# Imports
import Commands
import HatBotConfig
import logging
import socket
import time


class TwitchBot(object):
    """Twitch Bot Created by Hatmaster."""

    def __init__(self):
        config = HatBotConfig.HatBotConfig()
        self.can_send_messages = True
        self.connection_data = ("irc.chat.twitch.tv", 6667)
        self.oauth_token = config.loadOption(config.SECTION_CREDENTIALS, config.OPTION_OAUTH_TOKEN)
        self.bot_username = config.loadOption(config.SECTION_CREDENTIALS, config.OPTION_BOT_USERNAME)
        self.channel_name = "#" + config.loadOption(config.SECTION_CREDENTIALS, config.OPTION_CHANNEL_NAME).lower()

        self.is_logged_in = False
        self.is_connected = False
        self.server = socket.socket()
        self.stop = False

        self.debug_all_twitch_info = False

        if (self.is_connected is False):
            self.connect_until_success()

        if (self.is_connected):
            self.server.send(bytes('PASS ' + self.oauth_token + '\r\n', 'utf-8'))
            self.server.send(bytes('NICK ' + self.bot_username + '\r\n', 'utf-8'))
            self.server.send(bytes('CAP REQ :twitch.tv/tags\r\n', 'utf-8'))
            self.server.send(bytes('JOIN ' + self.channel_name + '\r\n', 'utf-8'))

            self.log("Joining Channel " + self.channel_name[1:] + "..")
        else:
            self.log("Failed to connect, check internet connection or settings.")

    def connect_until_success(self, max_attempts=20):
        """Connect to twitch until success or max_attempts is reached.

        Parameters
        ----------
        MAX_ATTEMPTS : TYPE, optional
            DESCRIPTION. The default is 20.

        Returns
        -------
        Boolean
            Whether the bot was able to connect or not.

        """
        success = False
        connect_attempts = 1
        while(self.is_connected is False):
            if (connect_attempts < max_attempts):
                try:
                    self.server.connect(self.connection_data)
                    self.is_connected = True
                    success = True
                    print("Connected.")
                except:
                    # Connetion failed.
                    self.log("Connection failed... trying again...")
                    time.sleep(2**connect_attempts)
                    connect_attempts += 1
            else:
                break
        return success

    # Send a message to the connected twitch channel via the twitch bot
    def send_message(self, message):
        """Send a message in connected Twitch Chat.

        Parameters
        ----------
        message : String
            Message to send.

        Returns
        -------
        None.

        """
        if (self.is_connected and self.can_send_messages):
            self.log(self.bot_username + " -> " + message)
            self.server.send(bytes('PRIVMSG ' + self.channel_name +
                                   ' :' + message + '\r\n', 'utf- 8'))

    def log(self, text):
        """Log text.

        Parameters
        ----------
        text : String
            Text to log.

        Returns
        -------
        None.

        """
        print(text, end='\n')

    def main(self):
        """Logic for main method for Twitch Bot."""
        if (self.is_connected and self.stop is False):
            self.server.settimeout(.05)
            try:
                rawdata = (self.server.recv(2048))
            except:
                # There is no data from twitch currently.
                return
            try:
                data_string = rawdata.decode("utf-8")
            except UnicodeDecodeError as e:
                data_string = ""
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

            if (self.is_logged_in is True):
                if (data_string != "" and "PRIVMSG" in data_string):
                    self.parseTags(data_string)

            if ("Welcome, GLHF!\r\n:tmi.twitch.tv" in data_string):
                self.is_logged_in = True
                self.log("Successfully logged into " + self.channel_name[1:] + "'s chat!")

    def exit_bot(self):
        """Exit and disconnect the Twitch Bot."""
        self.server.send(bytes('PART ' + self.channel_name + '\r\n', 'utf-8'))
        self.is_connected = False
        self.stop = True
        del self

    def parse_twitch_message(self, twitch_message_data):
        """Parse Data from Twitch into a user dictionary.

        When a message is received, tags start at the first '@'. After that,
        all tags have a name and an equals sign with the value being after the
        '='. At the very end there is a space with 'PRIVMSG #channel_name'.
        Using this information we are able to extract all tags and their values
        into a dictionary, then with the message at the very end.
        This varies for other events that are not messages but we mostly care
        about the messages.

        Parameters
        ----------
        twitch_message_data : String
            String of data returned by Twitch.

        Returns
        -------
        None.

        """
        tag_start = twitch_message_data.find("@")
        tag_end = twitch_message_data.find("PRIVMSG")-1
        # Sometimes twitch_message_data starts with multiple new lines. We avoid that by
        # skipping to the first @
        twitch_message_data = twitch_message_data[tag_start:]

        chat_message = None
        tag_start += 1  # Do not include the '@'
        # There is a twitch irc tags data being sent, could contain a chat message
        tags_dict = {}
        tags = twitch_message_data[tag_start:tag_end]
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
                self.check_command(tags_dict)
            else:
                print("SOMETHING WENT WRONG WITH DISPLAYNAME, CHATMESSAGE (", displayname, ", ", chat_message, ")", sep="")
                print("\t", twitch_message_data)

    def parseTags(self, data_string):
        tag_start = data_string.find("@")
        tag_end = data_string.find("PRIVMSG")
        if (tag_start != -1 and tag_end != -1):
            # Sometimes multiple messages are sent in twitch irc. Handle
            # Them by using recursion.
            newline_count = data_string.count("\n")

            for i in range(newline_count):
                twitch_message_data = data_string[tag_start:data_string.find("\n")+1]
                print("twitch_message_data:", twitch_message_data, end="--END\n")
                self.parse_twitch_message(twitch_message_data)
                data_string = data_string[data_string.find("\n")+1:]
                newline_count = data_string.count("\n")

    def log_twitch_message(self, displayname, message, displayname_color="#FFFFFF", list_emotes=None):
        """
        Log a twitch message to the console.

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

    def check_command(self, tags_dict):
        if ("chat_message" in tags_dict):
            #print("mod:", tags_dict['mod'], type(tags_dict['mod']), chatterPermission)
            chatMessage = tags_dict["chat_message"].rstrip("\n\r")
            params = chatMessage.split(" ")  # Split the message based on spaces
            command = params.pop(0).lower()  # Gets rid of the command name in params

            Commands.check_command(self, command, tags_dict, params)


def validate_token():
    valid = True
    config = HatBotConfig.HatBotConfig()
    oauth_token = config.loadOption(config.SECTION_CREDENTIALS, config.OPTION_OAUTH_TOKEN)
    if(oauth_token == None or not (oauth_token.startswith("oauth:"))):
        valid = False

    return valid


if __name__ == "__main__":
    print("Running", __file__, "as main method..")
    # Remove all handlers associated with the root logger object.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Reconfigure logging again, this time with a file.
    logging.basicConfig(level=logging.INFO, format='%(filename)s:%(lineno)s %(levelname)s:%(message)s')
    if (validate_token()):
        twitch_bot = TwitchBot()
        while(True):
            twitch_bot.main()
    else:
        print("invalid oauth token")
