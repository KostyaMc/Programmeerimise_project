import requests


url = "https://api.football-data.org/v4/matches"
headers = {"X-Auth-Token": "0969f3f7693f4b7a9803059c33490f65"}  # token for api
team_id = 4  # bvb id
competition_id = "CL"  # champions league id

response = requests.get(url, headers=headers)
data = response.json()

# BVB BD1 finished matches
try:
    if team_id:
        matches_url = f"https://api.football-data.org/v4/teams/{team_id}/matches?status=FINISHED"
        matches_response = requests.get(matches_url, headers=headers)
        matches_data = matches_response.json()

        print("\n Last 5 matches Borussia Dortmund:\n")
        for match in matches_data["matches"][-5:]:
            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]
            score = match["score"]["fullTime"]
            date = match["utcDate"][:10]
            print(f"{date} — {home} {score['home']} : {score['away']} {away}")
    else:
        print("team not found.")
except:
    print("Request from footballs API doesnt work")


# BVB CL finished matches
try:
    response = requests.get(f'https://api.football-data.org/v4/teams/{team_id}/matches?competitions={competition_id}&status=FINISHED', headers=headers, timeout=10)
       
    # status control
    response.raise_for_status()
    
    # parsing attempt JSON
    data = response.json()
    
    for match in data["matches"]:
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]
        score = match["score"]["fullTime"]
        time = match["utcDate"][:10]
        print(f"{time} — {home} {score['home']}:{score['away']} {away}")
except:
    print()