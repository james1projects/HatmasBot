#IMPORT PACKAGES
import HatBotConfig
import json
import os
from PIL import Image
import shutil
import sys

#Validate all directories for Character Requests
def ValidateDirectory():
    valid = True
    print("Validating Directories for Character Requests")
    config = HatBotConfig.HatBotConfig()
    dir_character_images = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.DIR_CHARACTER_IMAGES)
    if (not os.path.exists(dir_character_images)):
        print(dir_character_images, " does not exist. Creating Directory..")
        os.mkdir(dir_character_images)

    dir_files = config.loadOption(config.SECTION_SETTINGS, config.DIR_FILES)
    dir_stream_sources = config.loadOption(config.SECTION_SETTINGS, config.DIR_STREAM_SOURCES)
    
    myDirectories = [dir_files, dir_stream_sources]
    
    #Check for all needed directories and create them if they do not exist.
    for path in myDirectories:
        if (not os.path.isdir(path)):
            print(path, "does not exist, creating a new directory for it.")
            try:
                os.mkdir(path)
            except:
                print("Could not create a new directory for", path)
                valid = False
            
    path_character_list_json = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.PATH_CHARACTER_LIST_JSON)
    if (not os.path.exists(path_character_list_json)):
        print("character_list.json not found. Creating a new empty one.")
        characterList = []   #Create an empty character list
    else:
        characterList = LoadCharacterList()
    
    imageExtensions = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.CHARACTER_IMAGE_FORMATS).split("/")
    path_character_blank_image = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.PATH_CHARACTER_BLANK_IMAGE_SOURCE)
    for ext in imageExtensions:
        ext = "." + ext
        if (os.path.exists(path_character_blank_image + ext)):
            path_character_blank_image = path_character_blank_image + ext
            break
    if (not os.path.exists(path_character_blank_image)):
        CreateBlankImage()
    UpdateAllFiles(characterList)
    return valid
    
def CreateBlankImage():
    config = HatBotConfig.HatBotConfig()
    imageExtensions = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.CHARACTER_IMAGE_FORMATS).split("/")
    path_character_blank_image = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.PATH_CHARACTER_BLANK_IMAGE_SOURCE)
    for ext in imageExtensions:
        if (ext == 'gif'):
            continue
        path_character_blank_image = path_character_blank_image + "." + ext
        break
    
    img = Image.new("RGBA", (512, 512), (255, 255, 255, 0))
    img.save(path_character_blank_image, ext.upper())
    
#The initial way to add a new character to the request list
def RequestCharacter(rawCharacterName):
    rawCharacterName = rawCharacterName.lower()
    
    #Checks if the character is valid or is a nickname
    characterRequestName = LookUpCharacter(rawCharacterName)
    
    characterList = LoadCharacterList()
    characterList.append(characterRequestName)
    UpdateAllFiles(characterList)
    return True
    

#Checks if the character is a valid one.
def LookUpCharacter(characterRequestName):
    #TODO: Implement finding a character from a nicknames json file
    
    return characterRequestName.title()
    
#Gets the character list from the json file
def LoadCharacterList():
    config = HatBotConfig.HatBotConfig()
    path_character_list_json = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.PATH_CHARACTER_LIST_JSON)
    with open(path_character_list_json, "r") as inFile:
        character_list = json.load(inFile)
        
    return character_list

#Saves the character list to its json file
def SaveCharacterList(characterList):
    config = HatBotConfig.HatBotConfig()
    path_character_list_json = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.PATH_CHARACTER_LIST_JSON)
    with open(path_character_list_json, "w") as outFile:
        json.dump(characterList, outFile)

#Updates all files with a new characterList
def UpdateAllFiles(characterList):
    print("Updating all files for character requests...")
    SaveCharacterList(characterList)
    UpdateStreamSources(characterList)
    
#Updates Stream Sources for OBS
#Updates character list text
#Updates character next text & next image
def UpdateStreamSources(characterList = None):
    if (characterList == None):
        characterList = LoadCharacterList()
    
    #Updates the text file with the character list
    #Also updates the next character
    UpdateStreamSourceCharacterList(characterList)

#Updates the Character List Stream Source text file
def UpdateStreamSourceCharacterList(characterList):
    config = HatBotConfig.HatBotConfig()
    path_character_list_txt = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.PATH_CHARACTER_LIST_TXT)
    with open(path_character_list_txt, "w") as outfile:
        if (len(characterList) == 0):
            #The character list is empty.
            noCharacterListText = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.CHARACTER_RESPONSE_NO_LIST)
            outfile.write(noCharacterListText)
        else:
            for count, characterName in enumerate(characterList):
                characterName = characterName.title()
                #Formatted as (1 Request) (2 Request) ....
                outfile.write("(" + str(count + 1) + 
                              " " + characterName + ") ")
                
    UpdateStreamSourceCharacterNext(characterList)
                
                
#Updates the next character Stream Source text file & image
def UpdateStreamSourceCharacterNext(characterList):
    characterName = None
    config = HatBotConfig.HatBotConfig()
    characterType = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.CHARACTER_TYPE)
    
    path_character_next_txt = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.PATH_CHARACTER_NEXT_TXT)
    nextCharacterBlankText = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.CHARACTER_RESPONSE_NO_NEXT)
    with open(path_character_next_txt, "w") as outfile:
        if (len(characterList) == 0):
            #Character list is empty. Next character is nextCharacterBlankText
            outfile.write(nextCharacterBlankText)
        else:
            characterName = characterList[0].title()    #Capitalize the characterName
            #TODO: Change to be included in the config file.
            outfile.write("Next " + characterType + " Request:\n" + characterName)
    UpdateStreamSourceCharacterNextImage(characterName)
     
    
#Updates the Stream Source next character image for obs
def UpdateStreamSourceCharacterNextImage(characterName):
    config = HatBotConfig.HatBotConfig()
    imageExtensions = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.CHARACTER_IMAGE_FORMATS).split("/")
    #Check if that image exists
    if (characterName == None):
        #This path does NOT include an extension.
        path_character_image_source = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.PATH_CHARACTER_BLANK_IMAGE_SOURCE) 
    else:
        dir_character_images = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.DIR_CHARACTER_IMAGES)
        path_character_image_source = os.path.join(dir_character_images, characterName)
    if (not os.path.exists(path_character_image_source)):
        path_character_image_source = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.PATH_CHARACTER_BLANK_IMAGE_SOURCE) 
        
    for ext in imageExtensions:
        ext = "." + ext
        if (os.path.exists(path_character_image_source + ext)):
            path_character_image_source = path_character_image_source + ext
            break
    #Try copying the image.
    try:
        if (not os.path.exists(path_character_image_source)):
            path_character_image_source = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.PATH_CHARACTER_BLANK_IMAGE_SOURCE) 
            #just use the first non .gif extension
            for ext in imageExtensions:
                if (ext.lower() == "gif"):
                    continue
                ext = "." + ext
                path_character_image_source = path_character_image_source + ext
                break
        path_character_next_image = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.PATH_CHARACTER_NEXT_IMAGE)
        if (not os.path.exists(path_character_next_image + ext)):
            path_character_next_image = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.PATH_CHARACTER_NEXT_IMAGE)
            #just use the first non .gif extension
            for ext in imageExtensions:
                if (ext.lower() == "gif"):
                    continue
                ext = "." + ext
                path_character_next_image = path_character_next_image + ext
                break
        else:
            path_character_next_image = path_character_next_image + ext
        shutil.copy(path_character_image_source, path_character_next_image)
    except Exception as e:
        print("Error: cannot copy", path_character_image_source, "to\n", path_character_next_image, sep=" ")
        print(e)


#Remove a position from the character list, where the given position starts counting at 1
#Returns True if the removal was successful, False if it was not
def RemovePosition(position):
    result = False
    characterList = LoadCharacterList()
    index = position - 1
    if (index > len(characterList) - 1 or index < 0):
        result = False
    else:
        characterList.pop(index)
        UpdateAllFiles(characterList)
        result = True
        
    return result

#Replaces a position in the character list with a new character, where the position starts counting at 1
#Returns True if the replace was successful, False if it was not
def ReplacePosition(characterName, position):
    result = False
    characterList = LoadCharacterList()
    index = position - 1
    if (index > len(characterList) - 1 or index < 0):
        result = False
    else:
        characterList[index] = characterName
        UpdateAllFiles(characterList)
        result = True
        
    return result

#Inserts a character at the position in the character list, where the position starts counting at 1
#Returns True if the replace was successful, False if it was not
def InsertPosition(characterName, position):
    result = False
    characterList = LoadCharacterList()
    index = position - 1
    if (index > len(characterList) or index < 0):
        #The position is greater than the amount of characters in the List, or is less than 0.
        result = False
    else:
        characterList.insert(index, characterName)
        UpdateAllFiles(characterList)
        result = True
    
    return result

#Clears the character list to be empty
def ClearCharacterList():
    result = True
    characterList = []
    UpdateAllFiles(characterList)
    
    return result
    
def CharacterListToString():
    config = HatBotConfig.HatBotConfig()
    path_character_list_txt = config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.PATH_CHARACTER_LIST_TXT)
    with open(path_character_list_txt, "r") as infile:
        myString = infile.readline()

    return myString
    
#Purely for testing purposes
def main():
    if (ValidateDirectory()):
        ClearCharacterList()
#Used for testing purposes, only happens when this file is run by itself.
if __name__ == "__main__":
    main()