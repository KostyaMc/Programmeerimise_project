import requests
from bs4 import BeautifulSoup

#url = "https://api.football-data.org/v4/matches"
headers = {"X-Auth-Token": "0969f3f7693f4b7a9803059c33490f65"}
team_id = 4  # bvb id

#response = requests.get(url, headers=headers)
#data = response.json()

if team_id:
    matches_url = f"https://api.football-data.org/v4/teams/{team_id}/matches?status=FINISHED"
    matches_response = requests.get(matches_url, headers=headers)
    matches_data = matches_response.json()

    print("\n Последние 5 матчей Borussia Dortmund:\n")
    for match in matches_data["matches"]:
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]
        score = match["score"]["fullTime"]
        date = match["utcDate"][:10]
        print(f"{date} — {home} {score['home']} : {score['away']} {away}")
else:
    print("Команда не найдена.")