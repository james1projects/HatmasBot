"""Handles all basic Smite API requests and returns the data.

Can also save data to file.
"""

# Imports that are necessary for working with the Smite API and settings...
import HatBotConfig
import requests
import json
import hashlib
import os
from datetime import datetime
import time
import sys

# Paths
# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    curDir = os.path.dirname(sys.executable)
elif __file__:
    curDir = os.path.dirname(__file__)


path_getgodranks = os.path.join(curDir, 'smite API', 'json_files', 'godranks')
path_getgods = os.path.join(curDir, 'smite API', 'json_files', 'Gods.json')
path_getitems = os.path.join(curDir, 'smite API', 'json_files', 'Items.json')
path_getmotd = os.path.join(curDir, 'smite API', 'json_files', 'motd.json')
path_getdataused = os.path.join(curDir, 'smite API', 'json_files', 'dataused.json')
path_getgodskins = os.path.join(curDir, 'smite API', 'json_files', 'godskins')
path_getplayer = os.path.join(curDir, 'smite API', 'json_files', 'player')
path_searchplayers = os.path.join(curDir, 'smite API', 'json_files', 'searchplayers')
path_getRank = os.path.join(curDir, 'smite API', 'json_files', 'getrank')

SESSION_FAIL = 0
SESSION_SUCCESS = 1
SESSION_INVALID_DEV_ID = 2


# All function definitions in SmiteClient are purely for the purpose of getting
# information from the Smite API. Functions outside of this class but in this file
# are meant for processing it.
class SmiteClient(object):
    """Smite client used to connect to the Smite API."""

    RESPONSE_FORMAT = "json"

    def __init__(self, lang=1):
        # IMPORTANT PATHS
        self.path_smiteAPI = os.path.join(curDir, "smite API")
        if (not os.path.exists(self.path_smiteAPI)):
            os.mkdir(self.path_smiteAPI)
        self.path_jsonFiles = os.path.join(curDir, 'smite API', 'json_files')
        if (not os.path.exists(self.path_jsonFiles)):
            os.mkdir(self.path_jsonFiles)

        # Config Object for SmiteAPIConfig.ini
        config = HatBotConfig.HatBotConfig()

        self.devId = config.load_option(config.SECTION_SMITE_API, config.SMITE_API_DEV_ID, "")
        self.authKey = config.load_option(config.SECTION_SMITE_API, config.SMITE_API_AUTH_KEY, "")
        self.baseUrlPc = config.load_option(config.SECTION_SMITE_API, config.SMITE_API_PC_URL, "")
        self.sessionId = config.load_option(config.SECTION_SMITE_API, config.SMITE_API_SESSION_ID, "")

        self.lang = lang  # lang 1 is English
        self.load_session()

    def create_session(self):
        """Create a new session with the Smite API and saves it.

        :rtype: int
        :return: 0 for fail, 1 for success, 2 for invalid dev id
        """
        # Initialize the result to fail.
        result = SESSION_FAIL

        if (self.devId == "" or self.authKey == ""):
            # devId and authKey are not set properly.
            return result
        print("dev:", self.devId, "auth", self.authKey)
        signature = self.make_signature('createsession')  # Create a signature for creating the session

        # Create the url used for the Smite API
        url = '{0}/createsessionJson/{1}/{2}/{3}'.format(self.baseUrlPc, self.devId, signature, self.create_timestamp())
        # Request for the Smite API using the above URL
        req_result = requests.get(url)
        session = req_result.json()

        print("SESSION: ", session)
        if (session['ret_msg'] == 'Approved'):
            print("New Session Approved:" + str(session))
            self.sessionId = session['session_id']
            result = SESSION_SUCCESS
        elif(session['ret_msg' == 'Invalid Developer Id']):
            # The session reached the api servers but the developer id is incorrect.
            print("Invalid Developer Id.")
            result = SESSION_INVALID_DEV_ID
            self.sessionId = ""
        else:
            print("Creating Session NOT approved:", self.sessionId)
            self.sessionId = ""
            result = SESSION_FAIL

        self.save_session()
        return result

    def save_session(self):
        """Save the current session."""
        config = HatBotConfig.HatBotConfig()
        config.saveOption(config.SECTION_SMITE_API, config.SMITE_API_SESSION_ID,
                          self.sessionId)
        config.saveOption(config.SECTION_SMITE_API, config.SMITE_API_SESSION_DATETIME,
                          datetime.utcnow().isoformat())

    def load_datetime_session_created(self):
        """Load the datetime the last session was created."""
        config = HatBotConfig.HatBotConfig()

        session_created_datetime = config.load_option(
            config.SECTION_SMITE_API, config.SMITE_API_SESSION_DATETIME, "")
        if session_created_datetime != "":
            session_created_datetime = datetime.fromisoformat(session_created_datetime)

        return session_created_datetime

    def load_session(self):
        """Load the current session saved in config file.

        :rtype: String
        :return: sessionId
        """
        if (self.sessionId is None):
            # Session does not exist.
            self.create_session()

        if (self.devId == "" or self.authKey == ""):
            # devId and authKey are not set properly.
            return None

        config = HatBotConfig.HatBotConfig()
        self.sessionId = config.load_option(config.SECTION_SMITE_API, config.SMITE_API_SESSION_ID)
        session_created_datetime = self.load_datetime_session_created()
        now = datetime.utcnow()
        if (session_created_datetime == ""
                or (now - session_created_datetime).total_seconds() / 60 > 13):
            print("Old session is", (now - session_created_datetime).total_seconds() / 60, "minutes old.")
            # Session is becoming old. Create a new one.
            self.create_session_until_success()

        return self.sessionId

    def create_session_until_success(self, attempts=0):
        """Create a session until it is successful.

        :param attempts: (optional) The amount of times it has tried to create a new session,
        defaults to 0.
        :type attempts: int

        :rtype: boolean
        :return: success/fail
        """
        success = False
        MAX_ATTEMPTS = 15

        print("Trying to create a new session... attempt:", attempts, sep="")

        self.create_session()
        if (self.sessionId is None):
            if (attempts <= MAX_ATTEMPTS):
                time.sleep(.5)
                self.create_session_until_success(attempts + 1)
            else:
                print("\nCOULD NOT LOAD/CREATE A SUCCESSFUL SESSION!")
        else:
            success = True

        return success

    def build_request_url(self, method_name, parameters=[]):
        """Build the request url for the Smite API.

        :param method_name: The methodName for the API
        :type method_name: String
        :param parameters: List of Strings containing additional parameters in order.
        :type parameters: List of Strings

        :rtype: String
        :return: url
        """
        signature = self.make_signature(method_name)
        timestamp = self.create_timestamp()
        sessionId = self.sessionId
        devId = self.devId

        path = [method_name + self.RESPONSE_FORMAT, devId, signature, sessionId, timestamp]
        for param in parameters:
            path.append(str(param))

        url = self.baseUrlPc+'/'+'/'.join(path)
        print("\nBuilt request url:", url)

        return url

    def make_request(self, method_name, parameters=[]):
        """Make a request to the Smite API.

        :param method_name: The method name for the API
        :type method_name: String
        :param parameters: List of Strings of additional parameters in order. (optional)
        :type paramaeters: List of Strings

        :rtype: list
        :return: List (of possible dictionaries depending on request) for the request
        """
        # Initialize the final json file to be None
        result_json = None
        # Test the current session
        # test_result = self.test_session()
        # 0 is unsuccessful
        # 1 is successful
        # 2 is other
        test_result = self.test_session()
        if (test_result == 0 or test_result == 2):
            # Test was unsuccessful. Creating a new session.
            session_result = self.create_session_until_success()
            if (session_result == SESSION_SUCCESS):
                test_result = 1

        if(test_result == SESSION_SUCCESS):
            url = self.build_request_url(method_name, parameters)
            req_result = requests.get(url)
            if req_result.status_code == 200:
                result_json = req_result.json()
            elif req_result.status_code == 404:
                print("status code 404.")
            else:
                print(url + " Not Okay Status Code:", req_result.status_code)
            if result_json == []:
                print("\nRequest was successful, but returned no data.")
                print("result_json", result_json, req_result, '\n')
                result_json = None

        return result_json

    def test_session(self):
        """Tests the current session.

        :rtype: int
        :return: 0 for unsuccessful, 1 for successful, 2 for other
        """
        signature = self.make_signature('testsession')  # Makes a signature for testsession
        # result 0 is Unavailable
        # result 1 is Successful test
        # result 2 is other
        result = None

        url = '{0}/testsessionJson/{1}/{2}/{3}/{4}'.format(self.baseUrlPc, self.devId, signature, self.sessionId, self.create_timestamp())

        test_session = requests.get(url)
        print(test_session)
        test_session_json = test_session.json()
        if ("Service Unavailable" in test_session_json):
            print("Service Unavailble from testSession.")
            print(str(test_session))
            result = 0
        elif ("This was a successful test" in test_session_json):
            result = 1
        else:
            result = 2
            print(str(test_session))
            print("Other result from testSession.")

        return result

    def create_timestamp(self):
        """Creates a timestamp for right now

        :rtype: String
        :return: timestamp of when method is called"""
        return datetime.utcnow().strftime("%Y%m%d%H%M%S")

    def ping(self):
        """ping the server

        :rtype: json object
        :return: The request ping to the Smite API"""

        url = '{0}/pingJson'.format(self.baseUrlPc)
        req_ping = requests.get(url)
        return req_ping.json()

    def make_signature(self, method):
        """makes a signature for the API call. Uses self.create_timestamp()

        :rype: hashlib.md5 (String)
        :return: hashed signature for API"""
        time_stamp = self.create_timestamp()
        return hashlib.md5(self.devId.encode('utf-8') + method.encode('utf-8') + self.authKey.encode('utf-8') + time_stamp.encode('utf-8')).hexdigest()

    def get_hirez_server_status(self):
        """gets current hirez server status

        :rtype: list
        :return:  list of dictionaries for each server status"""
        request_json = self.make_request("gethirezserverstatus")

        return request_json

    # Get god ranks for a player
    # If myPath is set to None, a file path will be automatically generated
    def get_god_ranks(self, player, minutes=15):
        """gets the godranks for a player. SHOULD USE PLAYER ID BUT PLAYERNAME CAN BE USED INSTEAD

        :param player: the playerId (can use playerName but not as thoughough
        :type player: String

        :rtype: list
        :return: list of dictionaries all god stats for a player"""
        path_godRanks = os.path.join(self.path_jsonFiles, "godranks", player+".json")

        return self.load_json(path_godRanks, "getgodranks", parameters=[player], minutes=minutes)

    def get_match_details(self, match_id):
        """gets the match details with a matchId

        :param match_id: The match ID
        :type match_id: String

        :rtype: List
        :return: List of dictionaries for details in the specific match"""

        match_id = str(match_id)
        path_get_match_details = os.path.join(self.path_jsonFiles, "getMatchDetails", match_id+".json")
        match_details = self.load_json(path_get_match_details, 'getmatchdetails', parameters=[match_id], minutes=2)
        pretty_print(match_details)

        return match_details

    def get_match_player_details(self, match_id, minutes=30):
        """gets the player match details

        :param match_id: The match ID
        :type match_id: String
        :param minutes: How many minutes must pass before calling a request rather than reading the json file.
        :type minutes: int
        :rtype: List
        :return: List of dictionaries for player details in the specific match"""

        match_id = str(match_id)
        path_get_match_player_details = os.path.join(self.path_jsonFiles, "getMatchPlayerDetails", match_id + ".json")
        match_player_details = self.load_json(path_get_match_player_details, 'getmatchplayerdetails', [match_id], minutes=minutes)

        return match_player_details

    def get_items(self):
        """gets all item details from the Smite API for the current patch

        :rtype: List
        :return: List of dictionaries containing item details"""

        path_get_items = os.path.join(self.path_jsonFiles, "getItems.json")
        item_list = self.load_json(path_get_items, "getitems", [self.lang], 30)

        return item_list

    def get_gods(self):
        """gets all god information from the Smite API for the current patch

        :rtype: List
        :return: List of dictionaries containing god details"""
        path_get_gods = os.path.join(self.path_jsonFiles, "getGods.json")

        god_list = self.load_json(path_get_gods, "getgods", [self.lang], 1000)

        return god_list

    # Check if a file is older than the specified amount of time in minutes
    def is_file_old(self, path, minutes=12):
        """tests if a file is older than x minutes
        :param filePath: The file path to test.
        :type filePath: String (Path)
        :param minutes: If the file is older than x minutes, return True (default 12)
        :type minutes: int

        :rtype: Boolean:
        :return: Whether the file is old (True) or not (False)"""

        result = True
        if os.path.exists(path):
            secSinceModified = time.time() - os.path.getmtime(path)
            if (secSinceModified < minutes * 60):
                # The file is fresh.
                result = False

        return result

    # Save a json file for later requests instead of asking the API
    def save_json(self, path_json, req_json):
        # Do not save new results if the req_dict is None.
        if req_json == None or req_json == []:
            result = False
        else:
            with open(path_json, "w") as outFile:
                json.dump(req_json, outFile, indent=2)

            result = True
            print("Successfully saved", path_json)

        return result

    # Some API requests do not need to be made often at all! In fact, some only need to be made once in 12 minutes or even days
    # So intead we save these results and if the results are fresh, we just pull them from a saved json file instead!
    def load_json(self, path_json, method_name, parameters=[], minutes=12, new_request_required=False):
        """Tries to load the request from a saved json file, or creates a new request.

        :param path_json: The path to the specific saved json file.
        :type path_json: String (Path)
        :param method_name: The method name for the request.
        :type method_name: String
        :param parameters: List of parameters for request in order
        :type parameters: List (optional)
        :param minutes: The json file must be newer than minutes to read from file.
        :type minutes: int (defaults to 12)
        :param new_request_required: Whether to force a new request
        :type new_request_required: Boolean (defaults to False)

        :rtype: List
        :return: List (of possible dictionaries) for the request"""
        directory = os.path.dirname(path_json)

        if (not os.path.exists(directory)):
            print("Directory", directory, "does not exist. Creating it now.")
            os.mkdir(directory)

        if (self.is_file_old(path_json, minutes) or new_request_required):
            # File is old, lets make a new one.
            print(path_json, "is old, creating new one.")
            req_json = self.make_request(method_name, parameters)
            self.save_json(path_json, req_json)
        else:
            print(path_json, "already exists as a new json file, reading from there.")
            with open(path_json, 'r') as in_file:
                req_json = json.load(in_file)

        return req_json

    def get_motd(self):
        """Gets a list of Match Of The Days

        :rtype: List
        :return: List of dictionaries of match of the day"""
        motd_list = self.load_json(path_getmotd, 'getmotd', minutes=30)

        return motd_list

    def get_match_history(self, player_id):
        """Gets the match history for a playerId

        :rtype: List
        :return: List of dictionaries for a players match history"""
        match_history = self.make_request('getmatchhistory', [player_id])
        return match_history

    def get_player_status(self, player_id):
        """gets the status of a player

        :param player_id: The player ID
        :type player_id: String
        :rtype: List
        :return: list with dictionary of player status"""
        #0 - offline
        # 1 - In Lobby
        # 2 - God Selection
        # 3 - In Game
        # 4 - Online (player is logged in, but may be blocking broadcast of player state)
        # 5 - Unknown (player not found)"""
        path_player_status = os.path.join(self.path_jsonFiles, "getplayerstatus", player_id+".json")
        player_status = self.load_json(path_player_status, 'getplayerstatus', parameters=[player_id], minutes=.1)
        return player_status

    def search_players(self, player_name):
        """searches for a player

        :param player_name: The player name
        :type player_name: String

        :rtype: List
        :return: List with dictionary for search players result"""

        player_name = player_name.lower()
        path_search_players = os.path.join(self.path_jsonFiles, "searchplayers", player_name+".json")
        result = self.load_json(path_search_players, "searchplayers", [player_name], minutes=1200)

        return result

    def get_player(self, player, minutes=5):
        """get player, player can be player id or player but should be playerId
        :param player: The player/player id to find.
        :type player: String or int

        :rtype: List
        :return: List with dictionary for player"""

        player = str(player)  # Used if a player id is used
        path_player = os.path.join(self.path_jsonFiles, "getplayer", player + '.json')
        dict_player = self.load_json(path_player, 'getplayer', [player], minutes=minutes)

        return dict_player

    def get_player_id_by_name(self, player_name):
        """get player ID by name

        :param playerName: The player name
        :type playerName: String

        :rtype: dictionary
        :return: dictionary containing player info"""
        path_player_id_by_name_json = os.path.join(self.path_jsonFiles, "GetPlayerIdByName", player_name+'.json')
        dict_player = self.load_json(path_player_id_by_name_json, 'getplayeridbyname', [player_name], minutes=120)

        return dict_player

    def get_player_ids_by_gamertag(self, portal_id, gamertag):
        """Get player ids by gamer tag."""
        path_player_ids_by_gamertag = os.path.join(self.path_jsonFiles, "GetPlayerIdsByGamerTag", gamertag+".json")
        dic_result = self.load_json(path_player_ids_by_gamertag, 'getplayeridsbygamertag', [portal_id, gamertag], minutes=120)

        return dic_result

    def get_god_skins(self, god_id):
        """Get a list of god skins for a god id.

        Parameters
        ----------
        god_id : String
            String of god id

        Returns
        -------
        result : List
            List of dictionaries containing all skins for a god id.

        """
        result = None
        found_god = False
        all_gods_json = self.get_gods()
        for god in all_gods_json:
            if str(god["id"]) == str(god_id):
                found_god = True
                break
        if found_god:
            result = self.load_json(os.path.join(path_getgodskins, god_id+".json"), "getgodskins", [god_id, self.lang], minutes=1440)

        return result

    def get_data_used(self):
        """get data used for Smite API"""
        path_get_data_used = os.path.join(self.path_jsonFiles, "getDataUsed" + ".json")
        data_used = self.load_json(path_get_data_used, "getdataused", minutes=.1)

        return data_used

    def pretty_print(self, json_object):
        json_formatted_str = json.dumps(json_object, indent=2)
        print(json_formatted_str)


def pretty_print(json_object):
    json_formatted_str = json.dumps(json_object, indent=2)
    print(json_formatted_str)

if __name__ == "__main__":
    print("Running as main method.")
    smite_client = SmiteClient()