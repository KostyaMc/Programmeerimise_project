"""
Projekt: Jalgpalliklubide statistika
Autorid: Konstantin Geimonen ja Ruslan Nišajev

Kirjeldus:
Käesolev Django rakendus kuvab Borussia Dortmundi mängude statistikat,
sealhulgas viimaseid mänge, võitude, viikide ja kaotuste arvu ning
järgmise mängu tulemuse ennustust.

Mängude ennustamiseks kasutatakse lihtsat tehisintellekti mudelit,
mis põhineb Borussia Dortmundi 2024. aasta hooaja ajaloolistel andmetel.

Allikad:
- https://docs.djangoproject.com/en/5.2/
- https://realpython.com/python-requests/
"""

from django.shortcuts import render
from django.http import HttpResponse
import requests

# Tehisintellekti mudeli import
from .ai import model


# ===== Ennustuste tõlketabel (inglise → eesti) =====
PREDICTION_TRANSLATIONS = {
    "win": "Võit",
    "draw": "Viik",
    "lose": "Kaotus",
    "loss": "Kaotus",
}


# ===== Avalehe vaade =====
def index(request) -> HttpResponse:
    """
    Avalehe vaade.
    Kuvab:
    - Borussia Dortmundi viimased 5 mängu
    - Võitude, viikide ja kaotuste statistika
    - Järgmise mängu ennustuse (AI mudel)
    """

    # Football-Data API aadress lõppenud mängude jaoks
    url = "https://api.football-data.org/v4/teams/4/matches?status=FINISHED"
    headers = {"X-Auth-Token": "0969f3f7693f4b7a9803059c33490f65"}

    # Andmete pärimine API-st
    response = requests.get(url, headers=headers)
    matches_data = response.json()

    matches = []
    wins = 0
    draws = 0
    losses = 0

    # Viimase 5 mängu töötlemine
    for match in matches_data["matches"][-5:]:
        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]
        score = match["score"]["fullTime"]
        date = match["utcDate"][:10]

        # Mängu tulemuse määramine Borussia Dortmundi vaates
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

        # Mängu lisamine nimekirja
        matches.append({
            "date": date,
            "home": home,
            "away": away,
            "home_score": score["home"],
            "away_score": score["away"]
        })

    # Protsentuaalse statistika arvutamine
    total = wins + draws + losses or 1
    win_percent = round((wins / total) * 100, 1)
    draw_percent = round((draws / total) * 100, 1)
    loss_percent = round((losses / total) * 100, 1)


    # ===== Järgmise mängu ennustus =====
    url_next = "https://api.football-data.org/v4/teams/4/matches?status=SCHEDULED"
    response_next = requests.get(url_next, headers=headers)
    next_matches_data = response_next.json()

    bvb_prediction = None

    # Kui järgmine mäng on olemas
    if next_matches_data.get("matches"):
        next_match = next_matches_data["matches"][0]
        home = next_match["homeTeam"]["name"]
        away = next_match["awayTeam"]["name"]
        date = next_match["utcDate"][:10]

        is_home = home == "Borussia Dortmund"
        opponent = away if is_home else home

        # Tehisintellekti mudeli kasutamine ennustamiseks
        result = model.predict(opponent, is_home)

        # Ennustuse tõlkimine eesti keelde
        raw_prediction = result["prediction"].lower()
        translated_prediction = PREDICTION_TRANSLATIONS.get(
            raw_prediction, raw_prediction
        )

        # Ennustuse andmete ettevalmistamine mallile
        bvb_prediction = {
            "date": date,
            "home": home,
            "away": away,
            "opponent": opponent,
            "is_home": is_home,
            "prediction": translated_prediction,
            "confidence": f"{result['confidence']*100:.1f}%",
            "probabilities": {
                "win": result['probabilities']['win'] * 100,
                "draw": result['probabilities']['draw'] * 100,
                "lose": result['probabilities']['lose'] * 100,
            },
        }

    # Andmete edastamine HTML-mallile
    context = {
        "title": "Avaleht",
        "matches": matches,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "win_percent": win_percent,
        "draw_percent": draw_percent,
        "loss_percent": loss_percent,
        "bvb_prediction": bvb_prediction,
        "social_links": {
            "instagram": "https://www.instagram.com/bvb09/",
        },
    }

    return render(request, "main/index.html", context)


# ===== Meist-lehe vaade =====
def about(request):
    """
    Kuvab info veebilehe autorite ja projekti eesmärgi kohta
    """

    context = {
        "title": "Meist",
        "what_we_do": (
            "Meie eesmärk on luua kasutajasõbralik veebileht "
            "Borussia Dortmundi fännidele, pakkudes infot mängude, "
            "võitude, viikide ja kaotuste kohta ning statistilisi ülevaateid."
        ),
        "about_description": (
            "Oleme Tartu Ülikooli informaatika instituudi "
            "esimese kursuse tudengid – Konstantin Geimonen ja Ruslan Nišajev."
        ),
        "social_links": {
            "instagram": "https://www.instagram.com/bvb09/",
        },
        "emails": [
            "nisajev@ut.ee",
            "konstantin.geimonen@ut.ee",
        ],
    }

    return render(request, "main/about.html", context)


# ===== Meeskonna lehe vaade =====
def squad(request):
    """
    Kuvab Borussia Dortmundi praeguse meeskonna
    """

    context = {
        "title": "Meeskond",
        "social_links": {
            "instagram": "https://www.instagram.com/bvb09/",
        },
    }

    return render(request, "main/squad.html", context)
