from pyspark.sql import SparkSession
from pyspark.sql import Row
from pyspark.ml.recommendation import ALS

from web_crawler import get_user_info, game_detail

import json

class Recommendation:
    
    def __init__(self, steam_id, num_results) -> None:
        ''' 
        Constructor that initializes the Recommendation object
        with steam_id and num_results.   

        : param: steam_id: The user's 17-digit steam id entered in the textfield in index.html
        : param: num_results: The number of games recommended 
        '''
        self.steam_id = steam_id
        self.num_results = num_results
    

    def get_recommendations(self):
        '''
        Generate a list of recommended games using collaborative-based filtering. Collaborative-based 
        filtering takes users and games played in the past two weeks and use the hours played for each
        to determine the recommendation. 
        
        This method uses PySpark, a Python API for Apache Spark, and Alternating Least Squares, as the 
        algorithm, to produce recommendation  
        '''
        # Retrieve user information
        # Returns a dictionary with key: game id and value: hours played forever of game
        game_hours_dict = get_user_info(self.steam_id) 
        
        self.steam_id = 0
        list_of_user_games_hours = []
        # Place in format ((steam id, app id, hours played))
        for game in game_hours_dict:
            users_games_hours_tuple = (self.steam_id, int(game), game_hours_dict[game])
            list_of_user_games_hours.append(users_games_hours_tuple)

        # Retrieve the other users information in json file 
        json_path = "json/updated_user_game_hours.json"
        with open(json_path, 'r') as file:
            other_users_games_hours = json.load(file)

        list_other_users_games = [tuple(users) for users in other_users_games_hours]

        # Add list together
        list_user_game_hours = list_other_users_games + list_of_user_games_hours   

        # Train the ALS model 
        spark = SparkSession.builder.appName("Recommendation").getOrCreate()

        # Convert list_user_game_hours to Spark DataFrame
        steam_users_rdd = spark.sparkContext.parallelize(list_user_game_hours)
        df = steam_users_rdd.map(lambda x: Row(steam_id=x[0], app_id=x[1], hours=x[2])).toDF()

        # Building the recommendation model using ALS
        als = ALS(
            userCol="steam_id", 
            itemCol="app_id", 
            ratingCol="hours",
            nonnegative=True, 
            coldStartStrategy="drop"
        )

        # Split the data into training and test sets
        training, test = df.randomSplit([0.8, 0.2])
        
        # Fit the ALS model
        model = als.fit(training)

        user_recommendations = model.recommendForUserSubset(
            spark.createDataFrame([(self.steam_id,)], ["steam_id"]),  
            self.num_results  
        )

        recommendations = []
        for row in user_recommendations.collect(): 
            for rec in row['recommendations']:
                recommendations.append(rec['app_id'])
    
        return game_detail(recommendations)


    