from flask import Flask, redirect, url_for, render_template, request
from recommendation import Recommendation
import requests

# Create the flask application
app = Flask(__name__)

# Route for the home page
@app.route("/")
def home():
    return render_template("index.html")

# Route for sending user input   
@app.route("/recommendation", methods=["POST", "GET"])
def submit():
    if request.method == "POST":
        steam_id = request.form["steamID"]
        
        key = '93DF65A657503ACE0EE1E29B6746DA3B'
        url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={steam_id}"
        response = requests.get(url)
        data = response.json()
        if "response" in data and "players" in data["response"]:
            username = data["response"]["players"][0]["personaname"]
         
        # Retrieve the recommended games 
        recommended_games = steam_recommendation(steam_id)  
        
        # Render the recommendation page, passing the variables through it
        return render_template("recommendations.html", recommended_games=recommended_games, username=username) 
    else:
        return render_template("index.html")

def steam_recommendation(steam_id):
    num_results = 10
    # Instantiate Recommendation class 
    recommendation = Recommendation(steam_id, num_results)
    results = recommendation.get_recommendations()
    return results

if __name__ == "__main__":
    app.run(debug=True)