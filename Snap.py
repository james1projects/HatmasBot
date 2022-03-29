import requests
import json
import random

#Gets a list of half of the users in a twitch chat
def snap(twitchUsername):
    viewers = []
    mods = []
    vips = []
    snapped = []
    
    twitchUsername = twitchUsername.lower()
    URL = "http://tmi.twitch.tv/group/user/" + twitchUsername + "/chatters"
    chatterRequest = requests.get(url = URL)
    print(chatterRequest, URL)
    data = chatterRequest.json()

    chatter_count = data["chatter_count"]
    chatter_count -= 1 #Do not include broadcaster
    try:
        vips = data["chatters"]["vips"]
        print("vips:", vips)
    except:
        #There are no vips.
        print("There are no vips for snap.")
    try:
        mods = data["chatters"]["mods"]
    except:
        #There are no mods.
        print("There are no mods for snap.")
    try:
        viewers = data["chatters"]["viewers"]
    except:
        #There are no viewers.
        print("There are no chatters for snap.")
    #remove vips and mods from total chatter count
    viewers = viewers + vips
    chatter_count -= len(mods)
    
    random.shuffle(viewers)
    snapped = viewers[:round(chatter_count/2)]
    
    return snapped