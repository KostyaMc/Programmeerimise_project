"""
Projekt: Jalgpalliklubide statistika
Autorid: Konstantin Geimonen ja Ruslan Nišajev
Kirjeldus: Django veebiprojekt, mis kuvab jalgpalliklubide viimase viie mängu statistikat 
(näiteks võitude, viikide ja kaotuste arv ning nende protsentuaalne jaotus). 
Praegu on süsteemis olemas ainult Borussia Dortmundi andmed.
Kasutatud allikad:
https://youtu.be/qz0aGYrrlhU?si=ob0dm4BXOOYvvNGz
https://youtu.be/rHux0gMZ3Eg?si=zQLUXl79b16COGoq
https://docs.djangoproject.com/en/5.2/
https://realpython.com/python-requests/
"""

from django.shortcuts import render
from django.http import HttpResponse
import requests

from .ai import model

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


    # --- NEXT MATCH PREDICTION ---
    url_next = "https://api.football-data.org/v4/teams/4/matches?status=SCHEDULED"
    response_next = requests.get(url_next, headers=headers)
    next_matches_data = response_next.json()

    bvb_prediction = None  # initialize

    if next_matches_data.get("matches"):
        next_match = next_matches_data["matches"][0]  # get the very next match
        home = next_match["homeTeam"]["name"]
        away = next_match["awayTeam"]["name"]
        date = next_match["utcDate"][:10]

        is_home = home == "Borussia Dortmund"
        opponent = away if is_home else home

        # Use your AI model to predict the next match
        result = model.predict(opponent, is_home)
        bvb_prediction = {
            "date": date,
            "home": home,
            "away": away,
            "opponent": opponent,
            "is_home": is_home,
            "prediction": result['prediction'],
            "confidence": f"{result['confidence']*100:.1f}%",
            "probabilities": result['probabilities'],
        }

    # Send data to the template      
    context = {
        "title": "Home",
        "matches": matches,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "win_percent": win_percent,
        "draw_percent": draw_percent,
        "loss_percent": loss_percent,
        "bvb_prediction": bvb_prediction,  # next match prediction included
        'social_links': {
            'instagram': 'https://www.instagram.com/bvb09/',
        },
    }   

    return render(request, 'main/index.html', context)


# page About us
def about(request):
    
    context = {
        'title': 'About us',
        'content': 'This page contains basic information about the sites creators',
        'what_we_do': 'Our goal is to create a user-friendly website for fans of our beloved football team Borussia Dortmund, providing them with information about matches, number of wins, draws and losses, adding statistical insights for fans of this sport',
        'about_description': 'We are first-year students at the University of Tartu, Institute of Computer Science - Konstantin Geimonen and Ruslan Nishaev',
        'social_links': {
            'instagram': 'https://www.instagram.com/bvb09/',
        },
        'company_name': 'Borussia Dortmund',
        'email': 'service@bvb.de',
    }

    return render(request, 'main/about.html', context)

def squad(request):
    return render(request, 'main/squad.html')