from bs4 import BeautifulSoup
import requests
import re
import json
import time

def get_user_info(steam_id):
    ''' This method will retrieve the user's hours of
    games played in the past two weeks  '''

    # Steam key 
    key = '93DF65A657503ACE0EE1E29B6746DA3B'

    # Use the Steam API to retrieve info about recent games played
    url = 'https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key='+ key +'&steamid=' + steam_id + '&format=json'
    response = requests.get(url)
    data = response.json()
    
    try:
        games = data['response']['games']
    except:
        games = []

    # Dict contains games and hours played 
    list_games_hours = {}
    for game in games:
        list_games_hours[game['appid']] = game['playtime_forever']
    
    return list_games_hours

def store_user_info():
    ''' This method retrieves a list of the users and 
    call get_user_info() to retrieve the games and 
    hours played and store in a JSON file '''
    
    # Retrieve list of steam ID
    steam_list = get_user_id_list()
    
    user_game_hours_dict= {}

    # Iterate the list of steam users
    for steam_id in steam_list:
        list_games_hours = get_user_info(steam_id)
        user_game_hours_dict[steam_id] = list_games_hours
    
    # Store in JSON file
    json_path = "json/user_game_hours.json"
    with open(json_path, 'w') as file:
        json.dump(user_game_hours_dict, file)
        
def get_user_id_list():
    ''' This method will retrieve a list of steam id 
    from the URL'''

    # List of id of online steam users
    steam_id = [] 
    page_num = 1
    num_users = 100
 
    # Loop until list has num_users amount
    while len(steam_id) < num_users:            
        url = 'https://steamcommunity.com/games/steam/members?p=' + str(page_num)
        response = requests.get(url)
        doc = BeautifulSoup(response.text,'html.parser')
        users = doc.find_all('div', class_="friendBlock_in-game officerBlock")

        for user in users:
            user_profile_link = user.div.div.div.a['href'].encode("ascii").decode('utf-8')
            
            # Call get_user_id method to retrieve id and
            # append to the steam_id list
            id = get_user_id(user_profile_link)
            steam_id.append(id)  

            if len(steam_id) == num_users:
                break  

        page_num += 1

    return steam_id
    
def get_user_id(user_profile_link):
    ''' This method will retrieve the 17 digit steam ID
    by using the URL of the user '''

    # URL for a steam user 
    url = user_profile_link

    # Open the page     
    response = requests.get(url)
    doc = BeautifulSoup(response.text,'html.parser')

    # find steam ID 
    id = doc.find_all(['div'], role="main")
    user_id = str(id).split()[9]
    user_id = re.search("\"steamid\":\"(\d+)\"", user_id).group(1)
    
    # Return the steamID
    return user_id

def get_list_games():
    ''' This method will retrieve all the steam games ID'''
    
    # URL of all steam games
    url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    
    response = requests.get(url)
    
    data = response.json()
    apps = data['applist']['apps']
    apps_list = []

    for app in apps:
        apps_list.append(app['appid'])

    return apps_list

def game_detail(recommendations):
    ''' Get the game details and store then in a JSON file '''

    # Retrieve the list of app id 
    apps_list = recommendations
    # Dictionary to hold every game and the details
    game_detail_dict = {}
    
    for id in apps_list:
        # URL for details of each steam app
        url = 'https://store.steampowered.com/api/appdetails?appids=' + str(id) 
        time.sleep(0.0100)
        response = requests.get(url)
        data = response.json()

        details_dict = {}
        if data != None:
            for key in data:
                # Check if the success is true
                if data[key]["success"]:
                    # Check if the data is in the url 
                    # if true, then add to details_dict
                    if data[key]["data"]["name"]:
                        details_dict["name"] = data[key]["data"]["name"]
                    if data[key]["data"]["detailed_description"]:
                        details_dict["detailed_description"] = data[key]["data"]["detailed_description"]
                    if data[key]["data"]["header_image"]:
                        details_dict["header_image"] = data[key]["data"]["header_image"]
                    if data[key]["data"]["pc_requirements"]:
                        details_dict["pc_requirements"] = data[key]["data"]["pc_requirements"]
                    if data[key]["data"]["mac_requirements"]:
                        details_dict["mac_requirements"] = data[key]["data"]["mac_requirements"]
                    if data[key]["data"]["linux_requirements"]:
                        details_dict["linux_requirements"] = data[key]["data"]["linux_requirements"]
                    if "price_overview" in data[key]["data"]:
                        details_dict["price_overview"] = data[key]["data"]["price_overview"]["final_formatted"]                    
            game_detail_dict[id] = details_dict

    return game_detail_dict
        

def reformat_user_game_hours():
    ''' Reformat the user_game_hours for training
    to the format (steam id, app id, hours played) '''
    
    # Read from the user_game_hours.json file
    json_path = "json/user_game_hours.json"
    with open(json_path, 'r') as file:
        users_game_hours = json.load(file)
    
    list_of_users_games_hours = []

    for users in users_game_hours:
        if users_game_hours[users]:   
            for games in users_game_hours[users]:
                users_games_hours_tuple = (users, games, users_game_hours[users][games])
                list_of_users_games_hours.append(users_games_hours_tuple)
                
    with open(json_path, "w") as file:
        json.dump(list_of_users_games_hours, file, indent=4)


# Function calls
# store_user_info() # Store the users information about the games they played in the past two weeks(hours played)
# reformat_user_game_hours() # Reformat the user information (steam id, app id, hours played) so that it could be used for training

def map_id():
    ''' This function would map the steam_id to a number because 17-digit could not be processed in ALS'''
    json_path = "json/user_game_hours.json"
    with open(json_path, 'r') as file:
        data = json.load(file)

    user_ids = list(set(item[0] for item in data))
    id_mapping = {user_id: idx for idx, user_id in enumerate(user_ids, start=1)}
    for item in data:
        item[0] = id_mapping[item[0]]
        item[1] = int(item[1])

    json_path = "json/updated_user_game_hours.json"
    with open(json_path, 'w') as file:
        json.dump(data, file, indent=4)
    

#map_id()



