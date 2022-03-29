"""Contains all functions necessary for checking commands"""

import CommandsRequests
import commands_smite_api
import HatBotConfig
from mix_it_up_extended import MixClientExtended
import Snap
import time

class NotEnoughParameters(Exception):
    def __init__(self, msg):
        super().__init__(msg)

def getChatterPermission(twitchBot, tags_dict):
    broadcaster = twitchBot.channel_name[1:].lower()
    chatterPermission = 0
    if (tags_dict["mod"] == '0'):
        chatterPermission = 0
    if (tags_dict["subscriber"] == '1'):
        chatterPermission = 1
    if (tags_dict["mod"] == '1'):
        chatterPermission = 3
    if (tags_dict["display-name"].lower() == broadcaster):
        chatterPermission = 4

    return chatterPermission

def checkPermission(twitchBot, userPermission, neededPermission, user_dict, commandName):
    """Checks whether the user running the command has permission

    :oaran twutchBot: object twitchBot from class TwitchBot
    :type twitchBot: object
    :param userPermission: The current user's permission level
    :type userPermission: int
    :param neededPermission: The needed permission level to run the command
    :type neededPermission: int
    :param user_dict: Dictionary containing user info from twitch chat
    :type user_dict: dictionary
    :param commandName: The command being run
    :type commandName: String

    :rtype: Boolean
    :return: Whether the user has the correct permission or not"""

    userPermission = getChatterPermission(twitchBot, user_dict)
    #Permissions: 0, 1, 2, 3, 4 - User, Sub, VIP, Mod, Broadcaster
    hasPermission = False
    permissionType = ""
    if (userPermission >= neededPermission):
        #The user meets the permission requirements
        hasPermission = True
    else:
        print("User does not have permission!\n\t", user_dict)
        #User does NOT meet the permission requirements
        if (neededPermission == 1):
               permissionType = "sub"
        if (neededPermission == 2):
            permissionType = "VIP"
        if (neededPermission == 3):
               permissionType = "mod"
        if (neededPermission == 4):
            permissionType = "broadcaster"

        twitchBot.sendMessage("@" + user_dict["display-name"] +
                          ", you must be a " + permissionType + " to use " + commandName +
                          ".")
        hasPermission = False

    return hasPermission

def checkCommand(twitchBot, command, tags_dict, params):
    """checks any command being run by the Twitch Bot and does the appropriate action or response
    :param twitchBot: twitchBot object from class TwitchBot
    :type twitchBot: object
    :param command: The command name being sent.
    :type command: String
    :param tags_dict: dictionary response from twitch for message
    :type tags_dict:
    :param params: List of parameters
    :type params: List
    """
    command = command.lower()
    config = HatBotConfig.HatBotConfig()
    feature_character_request = config.loadBoolean(config.SECTION_TOGGLED_FEATURES, config.FEATURE_CHARACTER_REQUEST)
    feature_smite_api = config.loadBoolean(config.SECTION_TOGGLED_FEATURES, config.FEATURE_SMITE_API)
    feature_snap = config.loadBoolean(config.SECTION_TOGGLED_FEATURES, config.FEATURE_SNAP)
    if command.startswith("!"):
        print("Command:", command)
        try:
            if (feature_character_request):
                CommandsRequests.commandCharacterRequests(twitchBot, tags_dict, command, params)
            if (feature_smite_api):
                commands_smite_api.commands_smite_api(twitchBot, tags_dict, command, params)

            if feature_snap and command == "!snap":
                if (tags_dict["display-name"].lower() == twitchBot.channel_name[1:].lower()):
                    #The broadcaster typed !snap, let the snap commense!

                    #gets a list containing half of chatters, completely random and balanced as all things should be
                    list_snap = Snap.snap(twitchBot.channel_name[1:])
                    for user in list_snap:
                        # TODO add the duration and other settings to config file
                        twitchBot.sendMessage("/timeout " + user + " 720 Snapped")
                        time.sleep(0.3)

                    # TODO Change these messages to be based on the config file.
                    twitchBot.sendMessage("Perfectly Balanced. As all things should be BigGauntlet MonkaSnap (Half of users in chat have been timedout for 12 minutes)")
                else:
                    twitchBot.sendMessage("@" + tags_dict["display-name"] + ", Only " + twitchBot.channel_name[1:] + " has the Gauntlet.")
            elif command == "!gamble":
                # Gamble command
                if len(params) == 1:
                    mix_client = MixClientExtended()
                    gamble_amount = params[0]
                    message = mix_client.gamble(tags_dict["display-name"], gamble_amount)
                    if message == "":
                        message = "Use !gamble {amount}. Amount can be all, half, quarter, or a number."
                else:
                    message = "Use !gamble {amount}. Amount can be all, half, quarter, or a number."
                twitchBot.sendMessage(message)
        except Exception as e:
            print(e)