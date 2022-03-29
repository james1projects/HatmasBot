"""Processing Smite Api Commands."""

import Commands
import HatBotConfig
import SmiteAPIExtended


def is_string_valid_god(god_name, smite_client=None):
    """Check if a string is a Smite God.

    Parameters
    ----------
    god_name : TYPE
        DESCRIPTION.
    smite_client : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    String
        The spelling of the god in-game, or None if it is not found.

    """
    if smite_client is None:
        smite_client = SmiteAPIExtended.SmiteAPI()

    print('1')
    god_name = god_name.lower()
    god_list = smite_client.get_gods()

    for god_dictionary in god_list:
        if god_dictionary["Name"].lower() == god_name:
            # found the god!
            return god_dictionary["Name"]

    return None


def commands_smite_api(twitch_bot, tags_dict, command, params):
    """Process Smite Api Commands."""
    # TODO: Right now it does not detect VIPS, add that.
    # Permissions: 0, 1, 2, 3, 4 - User, Sub, VIP, Mod, Broadcaster
    user_level = 0
    sub_level = 1
    vip_level = 2
    mod_level = 3
    broadcaster_level = 4
    config = HatBotConfig.HatBotConfig()
    characterType = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.CHARACTER_TYPE)

    # lowercase all commands to make comparisons easier
    command = command.lower()
    # Load all commands from the config file.
    command_time_played = config.loadOption(config.SECTION_SMITE_API, config.COMMAND_TIME_PLAYED).lower()
    command_worshippers = config.loadOption(config.SECTION_SMITE_API, config.COMMAND_WORSHIPPERS).lower()
    command_duel_rank = config.loadOption(config.SECTION_SMITE_API, config.COMMAND_DUEL_RANK).lower()
    command_current_skin = config.load_option(config.SECTION_SMITE_API, config.COMMAND_CURRENT_SKIN, "")
    chatter_permission = Commands.getChatterPermission(twitch_bot, tags_dict)
    print("Smite API Command testing:", command, params)
    if command == command_time_played:
        # TIME PLAYED COMMAND
        if Commands.checkPermission(twitch_bot, chatter_permission, user_level, tags_dict, command):
            player_name = ""
            for p in params:
                player_name += p + " "

            player_name = player_name.rstrip(" ")
            if (player_name != ""):
                smite_client = SmiteAPIExtended.SmiteAPI()
                message = smite_client.get_readable_time_played(player_name)
            else:
                message = "Use " + command_time_played + " {Player}"

            twitch_bot.sendMessage(message)
    elif command == command_worshippers:
        # WORSHIPPERS COMMAND
        # !worshippers username god
        g = None
        if Commands.checkPermission(twitch_bot, chatter_permission, user_level, tags_dict, command):
            player_name = ""
            god_name = None
            temp_god_name = ""
            smite_client = SmiteAPIExtended.SmiteAPI()
            valid_god = False
            # Check all strings starting at the end of the paramaters to see if its a god. once a god is found, the rest up to the command
            # is part of the player name
            for i in range(len(params)):
                if len(params) == 1:
                    # Sometimes the command can be used without a god such as !worshippers hatmaster. In this case, just search for the player.
                    continue
                g = params.pop()
                temp_god_name = g + " " + temp_god_name
                temp_god_name = temp_god_name.rstrip(" ")
                temp_god_name = temp_god_name.strip(" ")

                temp = is_string_valid_god(temp_god_name, smite_client=smite_client)
                if (temp is not None):
                    valid_god = True
                    god_name = temp
                    break

            for p in params:
                player_name += p + " "

            if (valid_god is False and g is not None):
                player_name += " " + g
                player_name = player_name.rstrip(" ")

            player_name = player_name.rstrip(" ")
            if player_name != "":
                print(player_name, god_name)
                message = smite_client.get_readable_worshippers(player_name, god_name=god_name)
            else:
                message = "Please use " + command_worshippers + " {Player} {God}."

            twitch_bot.sendMessage(message)
    elif command == command_duel_rank:
        # Duel Rank Command:
        # !duelrank player_name

        if (Commands.checkPermission(twitch_bot, chatter_permission, user_level, tags_dict, command)):
            player_name = ""
            for p in params:
                player_name += p

            player_name = player_name.rstrip(" ")
            if (player_name != ""):
                smite_client = SmiteAPIExtended.SmiteAPI()
                message = smite_client.get_rank(player_name, "Duel")
            else:
                message = "Use " + command_duel_rank + " {Player}."

            twitch_bot.sendMessage(message)
    elif command == command_current_skin:
        # Get the streamers Smite username.
        streamer_smite_username = config.load_option(config.SECTION_SMITE_API, config.SMITE_USERNAME)
        if streamer_smite_username is not None:
            smite_client = SmiteAPIExtended.SmiteAPI()
            message = smite_client.get_readable_current_skin(streamer_smite_username)
            twitch_bot.sendMessage(message)
