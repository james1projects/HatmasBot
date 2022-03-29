"""Subclass of SmiteClient in module SmiteAPI.

Extracts data from the Smite API and transforms it into something useful for
HatBot or other uses..
"""

#Imports
import datetime
import hashlib
from PIL import Image
import json
import os
import math
import requests
import time
import shutil
import sys

import SmiteAPIConfig
from SmiteAPI import SmiteClient

if getattr(sys, 'frozen', False):
    curDir = os.path.dirname(sys.executable)
elif __file__:
    curDir = os.path.dirname(__file__)

class SmiteAPI(SmiteClient):
    def __init__(self):
        #Settings for any SmiteClient being made.
        self.rank_list = ["Unranked/Bronze III",
             "Bronze V",
             "Bronze IV",
             "Bronze III",
             "Bronze II",
             "Bronze I",
             "Silver V",
             "Silver IV",
             "Silver III",
             "Silver II",
             "Silver I",
             "Gold V",
             "Gold IV",
             "Gold III",
             "Gold II",
             "Gold I",
             "Platinum V",
             "Platinum IV",
             "Platinum III",
             "Platinum II",
             "Platinum I",
             "Diamond V",
             "Diamond IV",
             "Diamond III",
             "Diamond II",
             "Diamond I",
             "Masters",
             "Grandmaster"
        ]

        super().__init__()

    def get_current_playing_god(self, player_name):
        """Get the god the player is currently playing right now.

        :param player_name: The player name
        :type player_name: String

        :rtype: String
        :return: Dictionary with god and skin info.
        """
        player_dictionary = {}
        player_info = self.get_player_by_player_name(player_name)
        if player_info is None:
            # Could not find player.
            return player_dictionary
        player_dictionary['player_name'] = player_info.get('Name', player_name)
        player_dictionary['privacy_flag'] = player_info['privacy_flag']
        player_id = player_info['player_id']
        player_dictionary['player_id'] = player_id
        if player_dictionary['privacy_flag'] == 'y':
            return player_dictionary

        player_status_list = self.get_player_status(player_dictionary['player_id'])
        if (player_status_list is not None):
            player_status_info = player_status_list[0]
        else:
            return player_dictionary

        player_dictionary['status'] = player_status_info['status']
        match_id = player_status_info['Match']
        if (match_id != 0):
            # The player is in a match.
            match_details = self.get_match_player_details(match_id, minutes=1)
            if (match_details is not None):
                for p in match_details:
                    if (p["playerId"] == player_id):
                        # found player in match!
                        player_dictionary['god'] = p["GodName"]
                        player_dictionary['skin_id'] = p['SkinId']
                        player_dictionary['god_id'] = p['GodId']
                        break
        return player_dictionary

    def get_motd_today(self):
        """gets the match of the day for today

        :rtype: String
        :return: Match of the Day Name for Today"""
        motd = self.get_motd()
        current_day = datetime.date.today()

        formatted_date = '{d.month}/{d.day}/{d.year}'.format(d=current_day)
        #print("\n Formatted Date String:", formatted_date, "\n")
        for current_motd in motd:
            if (formatted_date in current_motd['startDateTime']):
                motd_today = current_motd['title']
                break

        return motd_today

    def get_player_by_player_name(self, player_name):
        """get player info by player username

        :param player_name: the player's name
        :type player_name: String

        :rtype: dictionary
        :return: dictionary with player information"""
        foundExactPlayer = False
        player = None

        player_name = player_name.lower()
        search_players = self.search_players(player_name)
        if search_players != None:
            for player in search_players:
                if player["hz_player_name"] != None:
                    current_player = player["hz_player_name"]
                else:
                    current_player = player["Name"]
                if current_player.lower() == player_name:
                    found_player = True
                    break
            if found_player == False:
                #Couldn't find the exact player but at least we can use the first result as it is almost always correct.
                player = search_players[0]

        return player

    def get_player_id_by_player_name(self, player_name):
        """gets a player ID by their player name

        :param player_name: the player's name
        :type player_name: String

        :rtype: String
        :return: The player ID"""
        player = self.get_player_by_player_name(player_name)
        player_id = player.get('player_id', None)

        return player_id

    def get_player_status_by_name(self, player_name):
        """gets the player status by player name

        :param player_name: The player's name
        :type player_name: String

        :rtype: List
        :return: List with dictionary of player status for playerName"""

        player_id = self.get_player_id_by_player_name(player_name)

        return self.get_player_status(player_id)

    #Get worshippers for a specific god for a player
    #If a god is not given, it returns their most worshipped god.
    def get_worshippers(self, player_name, god=None):
        """Returns worshippers for playerName with a specific god, or their top god

        :param player_name: The player name to find worshippers for
        :type player_name: string
        :param god: (optional) the god to find worshippers for
        :type god: String
        :return: dict_worshippers contains playerName, god, worshippers, privacy_flag
        Example:
        {
            'privacy_flag': 'n',
            'player name': 'Hatmaster',
            'god': 'Hou Yi',
            'worshippers': 5765,
            'found god': True
        }
        """

        player_info = self.get_player_by_player_name(player_name)
        worshippers_dict = {}
        found_god = False

        if (player_info is None):
            # No player found.
            return None

        worshippers_dict["privacy_flag"] = player_info["privacy_flag"]
        if player_info["hz_player_name"] != None:
            player_name = player_info["hz_player_name"]
        else:
            player_name = player_info["Name"]
        #Check if player is private
        if (player_info["privacy_flag"] == "y"):
            #Player has privacy flag on.
            return worshippers_dict


        player_id = player_info["player_id"]

        god_ranks = self.get_god_ranks(player_id)
        if god_ranks is None:
            return worshippers_dict
        if god is None:
            # use first god
            selected_god = god_ranks[0]
            found_god = True
            worshippers_dict['found god'] = True
        else:
            for selected_god in god_ranks:
                if (selected_god["god"].lower() == god.lower()):
                    found_god = True
                    worshippers_dict['found god'] = True
                    break
        worshippers = selected_god["Worshippers"]
        god = selected_god['god']
        worshippers_dict['player name'] = player_name

        if (found_god):
            worshippers_dict['god'] = god
            worshippers_dict['worshippers'] = worshippers
            worshippers_dict['found god'] = True
        else:
            #God was not found, find the most worshippers instead.
            worshippers_dict['found god'] = False

        return worshippers_dict

    def get_readable_worshippers(self, player_name, god_name=None):
        """Get worshippers for a player / god in a readable format.

        Parameters
        ----------
        player_name : String
            The player's name as a string
        god_name : String, optional
            The god name as a string. The default is None.

        Returns
        -------
        message : String
            Readable string for bot to send.

        """
        worshippers_dict = self.get_worshippers(player_name, god_name)
        print(worshippers_dict)
        if (worshippers_dict) is not None:
            player_name = worshippers_dict.get('player name', player_name)

            if worshippers_dict['privacy_flag'] == "y":
                message = player_name + " has their profile set to private."
            elif worshippers_dict.get('found god', False) is True:
                message = (player_name + " has " + str(worshippers_dict['worshippers']) +
                           " worshippers on " + worshippers_dict['god'] + ".")
            else:
                message = "Could not find worshippers for " + player_name + "."
        else:
            message = ("Could not find worshippers for " +
                       player_name + ".")

        return message



    def get_minutes_played(self, player_name):
        """gets how many minutes the player has played smite

        Parameters
        ----------
        player_name : String

        Returns
        -------
        minutes_played : int
        """
        minutes_played = None
        player_info = self.get_player_by_player_name(player_name)
        if player_info != None:
            player_id = player_info['player_id']
            player_name = player_info.get('Name', player_name)
            if player_info["privacy_flag"] == "n":
                if player_info["hz_player_name"] != None:
                    player_name = player_info["hz_player_name"]
                else:
                    player_name = player_info["Name"]
                player_id = player_info["player_id"]
                player_info = self.get_player(player_id)[0]
                minutes_played = player_info["MinutesPlayed"]
                minutes_played

        return [player_name, minutes_played]

    def get_readable_time_played(self, player_name):
        """returns a string of how much time a player has played in smite in a formatted message.


        Parameters
        ----------
        player_name : String

        Returns
        -------
        String

        """
        [player_name, minutes_played] = self.get_minutes_played(player_name)

        if (minutes_played == None):
           return player_name +" has not played Smite or has their profile hidden."

        if (minutes_played > 60):
            longer_than_hour = True
        else:
            longer_than_hour = False

        time_played_message = player_name + " has played Smite for "
        years = (int) (minutes_played / 60 / 24 / 365)
        if (years > 0):
            if (years == 1):
                suffix = ""
            else:
                suffix = "s"

            time_played_message += str(years) + " year" + suffix + ", "
            minutes_played -= (years * 365 * 24 * 60)
        days = (int) (minutes_played / 60 / 24)
        if (days > 0):
            if (days == 1):
                suffix = ""
            else:
                suffix = "s"
            time_played_message += str(days) + " day" + suffix + ", "
            minutes_played -= (days * 24 * 60)
        hours = (int) (minutes_played / 60)
        if (hours > 0):
            if (hours == 1):
                suffix = ""
            else:
                suffix="s"
            time_played_message += str(hours) + " hour" + suffix + ", "
            minutes_played -= (hours * 60)
        if (minutes_played > 0):
            if (minutes_played == 1):
                suffix = ""
            else:
                suffix = "s"

        if (longer_than_hour):
            time_played_message += "and "

        time_played_message += str(minutes_played) + " minute" + suffix + "."

        return time_played_message

    #Creates all smite god images from the gods.json file.
    #Uses official hirez god images.
    def create_smite_god_images(self):
        """Creates an image for every god in smite"""
        dir_god_images = os.path.join(curDir, "Smite API", "God Images")
        path_gods_file = os.path.join(self.path_jsonFiles, "getGods.json")

        if (not os.path.exists(dir_god_images)):
            os.mkdir(dir_god_images)

        with open(path_gods_file, "r") as god_file:
            dict_gods = json.load(god_file)
            #Loop through the dictionary containing all gods
            for god in dict_gods:
                url = (god["godIcon_URL"])
                god_name = god["Name"]
                path_cur_god_image = os.path.join(dir_god_images, god_name +'.png')
                #WRITE CROPPED IMAGES
                #image = Image.open(os.path.join(path_godImages, godName + ".png"))
                #box = (30, 30, 86, 86)
                #cropped_image = image.crop(box)
                #cropped_image.save(os.path.join(path_godImages, "cropped", godName + ".png"))

                if (not os.path.exists(path_cur_god_image)):
                    print("Creating " + god_name + " image using url: " + url)
                    #Open the url to the god image and save it as a file
                    response = requests.get(url)

                    with open(path_cur_god_image, "wb") as imageFile:
                        imageFile.write(response.content)

                    #WRITE STRETCHED IMAGES
                    path_stretchedImage = os.path.join(dir_god_images,  god_name + ".png")

                    image = Image.open(path_cur_god_image)
                    new_image = image.resize((512, 512))
                    new_image.save(path_stretchedImage)
                else:
                    print(god_name + " image already exists.")

    def get_skin_name_from_skin_id(self, god_id, skin_id):
        """Get a skin name from its skin id.

        Parameters
        ----------
        god_id : String
            god id for a god.
        skin_id : String
            Skin id for a skin.

        Returns
        -------
        :rtype: String
            The skin name.

        """
        skin_name = None
        skin_list = self.get_god_skins(god_id)
        # print("LOOKING FOR SKIN", skin_id, " IN \n", skin_list)
        for skin in skin_list:
            if str(skin['skin_id1']) == skin_id or str(skin['skin_id2']) == skin_id:
                skin_name = skin['skin_name']
                break

        return skin_name

    def get_readable_current_skin(self, player_name):
        """Get the current skin a player is using in a readable message.

        Parameters
        ----------
        player_name : String
            The player's name.

        Returns
        -------
        :rtype: String
            A formatted message of the skin the player is using.

        """
        message = 'Could not find player ' + player_name + '.'
        god_and_skin_dictionary = self.get_current_playing_god(player_name)
        if god_and_skin_dictionary.get('privacy_flag', None) == 'y':
            player_name = god_and_skin_dictionary['player_name']
            message = player_name + ' has their profile set to private.'
        elif god_and_skin_dictionary.get('privacy_flag', None) == 'n':
            if god_and_skin_dictionary.get("skin_id", None) is not None:
                god = god_and_skin_dictionary['god']
                god_id = str(god_and_skin_dictionary['god_id'])
                skin_id = str(god_and_skin_dictionary['skin_id'])
                player_name = str(god_and_skin_dictionary['player_name'])
                skin_name = self.get_skin_name_from_skin_id(god_id, skin_id)
                if skin_name is not None:
                    message = player_name + " is playing " + skin_name + " " + god + "."
            elif god_and_skin_dictionary.get('status', 5) == 0:
                message = player_name + ' is Offline.'
            elif god_and_skin_dictionary.get('status', 5) == 1:
                message = player_name + ' is in Lobby.'
            else:
                print("other player status:", god_and_skin_dictionary.get('status', 5))
                message = player_name + ' is not in a game right now.'

        return message

    def update_god_portrait(self, player_name, img_ext = ".png"):
        """Update the God Portrait for obs sources based on what god is being played.

        :param player_name: The player's name
        :type player_name: String
        :param img_ext: The image extension
            Defaults to '.png'
        :type img_ext: String

        :rtype: int
        :return: The recommended amount of miliseconds to delay before calling the function again.
        """
        dir_godImages = os.path.join(curDir, "Smite API", "God Images")
        if (not os.path.exists(dir_godImages)):
            os.mkdir(dir_godImages)
        dir_streamSources = os.path.join(curDir, "stream sources")
        if (not os.path.exists(dir_streamSources)):
            os.mkdir(dir_streamSources)

        delay = 60
        # TODO add all of these to the config file...
        path_sourceBlankImage = os.path.join(dir_streamSources, "blank image" + img_ext)
        path_streamPortraitImage = os.path.join(dir_streamSources, "Portrait Image" + img_ext)
        path_streamPortraitBacground = os.path.join(dir_streamSources, "Portrait Background" + img_ext)
        path_sourcePortraiBackground = os.path.join(dir_streamSources, "default portrait background" + img_ext)

        current_god_dictionary = self.get_current_playing_god(player_name)
        print(current_god_dictionary)
        god_name = current_god_dictionary.get('god', None)
        status = current_god_dictionary.get('status', 5)
        if status == 0:
            # Player is offline
            # Set delay to 10 minutes.
            delay = 600
        elif status == 1:
            # Player is in lobby, set delay to 2 minutes
            delay = 120
        elif status == 2:
            # Player is in god selection, update in 35 seconds.
            delay = 35
        elif status == 3:
            delay = 150
            pass
        if god_name is None:
            if (not os.path.exists(path_sourceBlankImage)):
                img = Image.new("RGBA", (512, 512), (255, 255, 255, 0))
                img.save(path_sourceBlankImage, "PNG")

            if (not os.path.exists(path_sourcePortraiBackground)):
                imgSize = (512, 512)
                img = Image.new("RGB", imgSize, (0, 0, 0))
                innerColor = [40, 0, 0] #Color at the center
                outerColor = [2, 0, 0] #Color at the corners

                for y in range(imgSize[1]):
                    for x in range(imgSize[0]):

                        #Find the distance to the center
                        distanceToCenter = math.sqrt((x - imgSize[0]/2) ** 2 + (y - imgSize[1]/2) ** 2)

                        #Make it on a scale from 0 to 1
                        distanceToCenter = float(distanceToCenter) / (math.sqrt(2) * imgSize[0]/2)

                        #Calculate r, g, and b values
                        r = outerColor[0] * distanceToCenter + innerColor[0] * (1 - distanceToCenter)
                        g = outerColor[1] * distanceToCenter + innerColor[1] * (1 - distanceToCenter)
                        b = outerColor[2] * distanceToCenter + innerColor[2] * (1 - distanceToCenter)


                        #Place the pixel
                        img.putpixel((x, y), (int(r), int(g), int(b)))

                img.save(path_sourcePortraiBackground, "PNG")
            shutil.copyfile(path_sourceBlankImage, path_streamPortraitImage)
            shutil.copyfile(path_sourceBlankImage, path_streamPortraitBacground)
            print("Set to blank image")
        else:
            print("copying smite portrait")
            path_sourcePortraitImage = os.path.join(dir_godImages, god_name+img_ext)
            shutil.copyfile(path_sourcePortraitImage, path_streamPortraitImage)
            shutil.copyfile(path_sourcePortraiBackground, path_streamPortraitBacground)

        return delay

    def get_joust_rank(self, player):
        return self.get_rank(player, "Joust")

    def get_conquest_rank(self, player):
        return self.get_rank(player, "Conquest")

    def get_duel_rank(self, player):
        return self.get_rank(player, "Duel")

    def get_rank(self, player, gamemode="Duel"):
        """Get the rank of a player in a gamemode.

        Parameters
        ----------
        player : String
            Player name
        gamemode : String, optional
            DESCRIPTION. The default is "Duel".

        Returns
        -------
        rank_message : String
            The player's rank as a readable string.

        """
        rank_message = ""

        pcTotal = 0
        pcWins = 0
        pcLosses = 0
        pcRank = 0
        pcMmr = 0

        consoleTotal = 0
        consoleWins = 0
        consoleLosses = 0
        consoleMmr = 0
        consoleRank = 0

        platform = {
                "Hi-Rez": "1",
                "Steam": "5",
                "PS4": "9",
                "Xbox": "10",
                "Switch": "22",
                "Discord": "25",
                "Epic": "28"
            }
        player_info = self.get_player_by_player_name(player)
        if player_info is not None and player_info != []:
            player = player_info.get("Name", player)
            if player_info["privacy_flag"] == "y":
                rank_message = player + " has their profile hidden."
            else:
                player_id = player_info["player_id"]
                player_list = self.get_player(player_id)

                player_dict = player_list[0]

                pcWins = player_dict["Ranked"+gamemode]["Wins"]
                pcLosses = player_dict["Ranked"+gamemode]["Losses"]
                pcTotal = pcWins + pcLosses

                consoleWins = player_dict["Ranked" + gamemode + "Controller"]["Wins"]
                consoleLosses = player_dict["Ranked" + gamemode + "Controller"]["Losses"]
                consoleTotal = consoleWins + consoleLosses

                if pcTotal >= consoleTotal:
                    if pcTotal == 0:
                        rank_message = player + " has not played any Ranked " + gamemode + " this split."
                    else:
                        tier = player_dict["Ranked" + gamemode]["Tier"]
                        pcRank = self.rank_list[tier]
                        pcMmr = round(player_dict["Ranked" + gamemode]["Rank_Stat"])
                        rank_message = player + " Ranked PC " + gamemode + ": " + pcRank + " - " + str(pcMmr) + " MMR"
                else:
                    if consoleTotal == 0:
                        rank_message = player + " has not played any Ranked " + gamemode + " this split."
                    else:
                        tier = player_dict["Ranked" + gamemode+"Controller"]["Tier"]
                        consoleRank = self.rank_list[tier]
                        consoleMmr = round(player_dict["Ranked" + gamemode+"Controller"]["Rank_Stat"])
                        rank_message = player + " Ranked Controller " + gamemode + ": " + consoleRank + " - " + str(consoleMmr) + " MMR"

        else:
            rank_message = "Could not find " + player + "'s profile."

        return rank_message


def pretty_print(json_object):
    json_formatted_str = json.dumps(json_object, indent=2)
    print(json_formatted_str)

def main():
    objSmiteClient = SmiteAPI()
    print(objSmiteClient.update_god_portrait("Hatmaster"))
if __name__ == "__main__":
    main()
