from django.shortcuts import render
from django.http import HttpResponse
import requests

# Home Page
def index(request) -> HttpResponse:
    # API setup
    url = "https://api.football-data.org/v4/teams/4/matches?status=FINISHED"
    headers = {"X-Auth-Token": "0969f3f7693f4b7a9803059c33490f65"}


    # Get the data from the API
    response = requests.get(url, headers=headers)
    matches_data = response.json()

    matches = []
    wins = 0
    draws = 0
    losses = 0

    # Last 5 matches
    for match in matches_data["matches"][-5:]:
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]
        score = match["score"]["fullTime"]
        date = match["utcDate"][:10]

        # Understand if the team has won/lost/drawn
        if home == "Borussia Dortmund":
            if score["home"] > score["away"]:
                wins += 1
            elif score["home"] == score["away"]:
                draws += 1
            else:
                losses += 1
        elif away == "Borussia Dortmund":
            if score["away"] > score["home"]:
                wins += 1
            elif score["away"] == score["home"]:
                draws += 1
            else:
                losses += 1


        matches.append({
            "date": date,
            "home": home,
            "away": away,
            "home_score": score["home"],
            "away_score": score["away"]
        })


    total = wins + draws + losses or 1
    win_percent = round((wins / total) * 100, 1)
    draw_percent = round((draws / total) * 100, 1)
    loss_percent = round((losses / total) * 100, 1)  


    # Send data to the template      
    context = {
        "title": "Home",
        "matches": matches,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "win_percent": win_percent,
        "draw_percent": draw_percent,
        "loss_percent": loss_percent
    }   
    

    return render(request, 'main/index.html', context)


def about(request):
    context = {
        'title': 'About us',
        'content': 'This page contains basic information about the sites creators',
        'text_on_page': 'НАДО ПРИДУМАТЬ И ДОБАВИТЬ'
    }

    return render(request, 'main/about.html', context)