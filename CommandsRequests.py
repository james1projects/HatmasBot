import Commands
import HatBotConfig
import CharacterRequests

def commandCharacterRequests(twitchBot, tags_dict, command, params):
    """commandCharacterRequests
    :param twitchBot: twitchBot object from class TwitchBot
    :type twitchBot: object
    :param tags_dict: dictionary response from twitch for message
    :type tags_dict:
    :param command: The command name being sent.
    :type command: String
    :param params: List of strings of additional parameters
    :type param: List
    """

    #TODO: Right now it does not detect VIPS, add that.
    #Permissions: 0, 1, 2, 3, 4 - User, Sub, VIP, Mod, Broadcaster
    userLevel = 0
    subLevel = 1
    vipLevel = 2
    modLevel = 3
    broadcasterLevel = 4
    config = HatBotConfig.HatBotConfig()
    characterType = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.CHARACTER_TYPE)

    #lowercase all commands to make comparisons easier
    command = command.lower()
    #Load all commands from the config file.
    requestCommand = config.loadOption(config.SECTION_CHARACTER_REQUEST_COMMANDS, config.COMMAND_CHARACTER_REQUEST).lower()
    removeCommand = config.loadOption(config.SECTION_CHARACTER_REQUEST_COMMANDS, config.COMMAND_CHARACTER_REMOVE).lower()
    replaceCommand = config.loadOption(config.SECTION_CHARACTER_REQUEST_COMMANDS, config.COMMAND_CHARACTER_REPLACE).lower()
    insertCommand = config.loadOption(config.SECTION_CHARACTER_REQUEST_COMMANDS, config.COMMAND_CHARACTER_INSERT).lower()
    showListCommand = config.loadOption(config.SECTION_CHARACTER_REQUEST_COMMANDS, config.COMMAND_CHARACTER_LIST).lower()
    howToRequestCommand = config.loadOption(config.SECTION_CHARACTER_REQUEST_COMMANDS, config.COMMAND_CHARACTER_HOW_TO_REQUEST).lower()
    clearCommand = config.loadOption(config.SECTION_CHARACTER_REQUEST_COMMANDS, config.COMMAND_CHARACTER_CLEAR).lower()

    chatterPermission = Commands.get_chatter_permission(twitchBot, tags_dict)
    #CHECK IF THE MESSAGE IS A REQUEST COMMAND
    if (command == requestCommand):
        #REQUEST COMMANDS
        if (Commands.check_permission(twitchBot, chatterPermission, modLevel, tags_dict, command)):
            #The chatter is a mod running this command.
            try:
                if (len(params) < 1):
                    print("params:", params)
                    raise Commands.NotEnoughParameters("Not enough paramaters provided to request command: " + str(command) + ' ' + str(params))

                characterName = params.pop(0)
                for word in params:
                    characterName += " " + word

                characterName = characterName.title()
                isRequested = CharacterRequests.RequestCharacter(characterName)
                #print("requesting " + characterName)
                if (isRequested):
                    twitchBot.send_message("Added " + characterName + " to the request list.")
                else:
                    twitchBot.send_message("Unable to add " + characterName + " to the request list.")
            except Exception as e:
                print(e)
                #Not enough paramaters were supplied.
                twitchBot.send_message("Use '" + requestCommand + " " +
                                      characterType + " Name' to add a " +
                                      characterType + " to the request list.")

    elif (command == removeCommand):
        #Remove COMMAND
        if (Commands.check_permission(twitchBot, chatterPermission, modLevel, tags_dict, command)):
                #The chatter is a mod running this command.
                try:
                    if (len(params) != 1):
                        raise Commands.NotEnoughParameters("Remove requires exactly one parameter: " + str(command) + ' ' +str(params))
                    position = int(params[0])
                    isRemoved = CharacterRequests.RemovePosition(position)
                    if (isRemoved):
                        twitchBot.send_message("Removed position " + str(position) + " from the request list.")

                except Exception as e:
                    print(e)
                    #Not enough paramaters were supplied.
                    twitchBot.send_message("Use '" + removeCommand + " " +
                                      " Position' to Remove a " +
                                      characterType + " from the request list.")
    elif (command == replaceCommand):
        #Replace COMMAND
        #Check the user's permission level.
        if (Commands.check_permission(twitchBot, chatterPermission, modLevel, tags_dict, command)):
            try:
                if (len(params) < 2):
                    raise Commands.NotEnoughParameters("Replace requires at least 2 parameters: " + str(command) + ' ' + str(params))

                position = int(params.pop(0))

                characterName = params.pop(0)

                for word in params:
                    characterName += " " + word

                isReplaced = CharacterRequests.ReplacePosition(characterName, position)
                if (isReplaced):
                    print("Replacing position " + str(position))
                    twitchBot.send_message("Replaced position " + str(position) + " with " + characterName)

            except Exception as e:
                print(e)
                twitchBot.send_message("Use '" + replaceCommand + " " +
                                'position' + characterType + ' Name'
                                " to Replace a " + characterType + " from the request list.")
    elif (command == insertCommand):
        #INSERT COMMAND
        if (Commands.check_permission(twitchBot, chatterPermission, modLevel, tags_dict, command)):
            try:
                if (len(params) < 2):
                    raise Commands.NotEnoughParameters("Insert requires at least 2 parameters: " + str(command) + ' ' + str(params))

                position = int(params.pop(0))

                characterName = params.pop(0)

                for word in params:
                    characterName += " " + word

                isInserted = CharacterRequests.InsertPosition(characterName, position)
                if (isInserted):
                    twitchBot.send_message("Inserted " + characterName + " at " +
                    str(position) + " to the request list.")
            except Exception as e:
                print(e)
                twitchBot.send_message("Use '" + insertCommand + " {" +
                                      characterType + " name} {position} to insert a " + characterType + " to the list.")

    elif (command == showListCommand):
        if (Commands.check_permission(twitchBot, chatterPermission, userLevel, tags_dict, command)):
            characterListString = CharacterRequests.CharacterListToString()
            twitchBot.send_message(characterListString)
    elif (command == howToRequestCommand):
        if (Commands.check_permission(twitchBot, chatterPermission, userLevel, tags_dict, command)):
            myString = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.CHARACTER_RESPONSE_HOW_TO_REQUEST)
            twitchBot.send_message(myString)
    elif (command == clearCommand):
        if (Commands.check_permission(twitchBot, chatterPermission, userLevel, tags_dict, command)):
            isCleared = CharacterRequests.ClearCharacterList()

            if (isCleared):
                twitchBot.send_message("Cleared the request list.")
            else:
                twitchBot.send_message("Failed to clear the request list.")