import pandas as pd
import numpy as np
from collections import Counter
import random
import os


# ===== Andmete laadimine =====

# Projekti baaskataloogi leidmine
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# CSV-faili asukoht
csv_path = os.path.join(BASE_DIR, 'data', 'bvb-2024.csv')

# Andmete lugemine CSV-failist
data = pd.read_csv(csv_path, encoding='cp1251', delimiter=',')

# Esimeste ridade kuvamine kontrolliks
print("Esimesed andmeread:")
print(data.head())


# ===== Sihtmuutuja loomine (võit / viik / kaotus) =====
def get_match_result(row):
    """
    Funktsioon määrab Borussia Dortmundi mängu tulemuse:
    - 'win'  → võit
    - 'draw' → viik
    - 'lose' → kaotus
    """

    home_team = str(row['Home Team'])
    away_team = str(row['Away Team'])

    # Kui Borussia Dortmund on kodumeeskond
    if 'Borussia Dortmund' in home_team:
        goals = str(row['Result']).split(' - ')
        if len(goals) == 2:
            fthg, ftag = int(goals[0]), int(goals[1])
            if fthg > ftag:
                return 'win'
            elif fthg == ftag:
                return 'draw'
            else:
                return 'lose'

    # Kui Borussia Dortmund on külalismeeskond
    elif 'Borussia Dortmund' in away_team:
        goals = str(row['Result']).split(' - ')
        if len(goals) == 2:
            fthg, ftag = int(goals[0]), int(goals[1])
            if ftag > fthg:
                return 'win'
            elif ftag == fthg:
                return 'draw'
            else:
                return 'lose'

    return None


# Uue veeru lisamine andmetesse (BVB_Result)
data['BVB_Result'] = data.apply(get_match_result, axis=1)

# Ainult Borussia Dortmundi mängude filtreerimine
bvb_matches = data[data['BVB_Result'].notna()].copy()

print(f"\nMängude koguarv: {len(bvb_matches)}")
print("Tulemuste jaotus:")
print(bvb_matches['BVB_Result'].value_counts())


# ===== Lihtne statistiline mudel =====
class SimpleBVBModel:
    """
    Lihtne statistiline mudel Borussia Dortmundi mängude ennustamiseks
    """
    def __init__(self):
        self.stats = {}
        self.overall_stats = {}

    def fit(self, data):
        """
        Mudeli treenimine ajalooliste andmete põhjal
        """

        # Üldine statistika (kõik mängud)
        self.overall_stats = dict(data['BVB_Result'].value_counts())
        total_matches = len(data)

        for result in self.overall_stats:
            self.overall_stats[result] /= total_matches

        # Kodus ja võõrsil mängude statistika
        home_stats = data[data['Home Team'].str.contains('Borussia Dortmund')]['BVB_Result'].value_counts()
        away_stats = data[data['Away Team'].str.contains('Borussia Dortmund')]['BVB_Result'].value_counts()

        self.stats['home'] = {}
        self.stats['away'] = {}

        for result in ['win', 'draw', 'lose']:
            self.stats['home'][result] = home_stats.get(result, 0) / len(home_stats) if len(home_stats) > 0 else 0
            self.stats['away'][result] = away_stats.get(result, 0) / len(away_stats) if len(away_stats) > 0 else 0

        # Vastaste tugevuse alusel
        strong_teams = ['Bayern', 'Leipzig', 'Leverkusen', 'Stuttgart', 'Frankfurt']
        medium_teams = ['Wolfsburg', 'Gladbach', 'Hoffenheim', 'Augsburg', 'Freiburg']

        self.stats['vs_strong'] = self._calculate_opponent_stats(data, strong_teams)
        self.stats['vs_medium'] = self._calculate_opponent_stats(data, medium_teams)
        self.stats['vs_weak'] = self._calculate_opponent_stats(
            data, [], exclude=strong_teams + medium_teams
        )

        return self

    def _calculate_opponent_stats(self, data, team_list, exclude=None):
        """
        Arvutab statistika vastaste tugevuse alusel
        """
        if exclude is None:
            exclude = []

        opponent_matches = []

        for _, row in data.iterrows():
            if 'Borussia Dortmund' in str(row['Home Team']):
                opponent = str(row['Away Team'])
            else:
                opponent = str(row['Home Team'])

            if team_list:
                if any(team in opponent for team in team_list):
                    opponent_matches.append(row['BVB_Result'])
            else:
                if not any(excl_team in opponent for excl_team in exclude):
                    opponent_matches.append(row['BVB_Result'])

        # Kui andmeid pole piisavalt, tagastame vaikimisi väärtused
        if not opponent_matches:
            return {'win': 0.33, 'draw': 0.33, 'lose': 0.34}

        stats = Counter(opponent_matches)
        total = len(opponent_matches)

        return {result: stats.get(result, 0) / total for result in ['win', 'draw', 'lose']}

    def predict(self, opponent, is_home=True):
        """
        Ennustab järgmise mängu tulemuse ja tõenäosused
        """

        strong_teams = ['Bayern', 'Leipzig', 'Leverkusen', 'Stuttgart', 'Frankfurt']
        medium_teams = ['Wolfsburg', 'Gladbach', 'Hoffenheim', 'Augsburg', 'Freiburg']

        # Vastase tugevuse määramine
        if any(team in opponent for team in strong_teams):
            opponent_stats = self.stats['vs_strong']
        elif any(team in opponent for team in medium_teams):
            opponent_stats = self.stats['vs_medium']
        else:
            opponent_stats = self.stats['vs_weak']

        # Kodus või võõrsil mängimise statistika
        location_stats = self.stats['home' if is_home else 'away']

        # Kombineeritud tõenäosuste arvutamine
        combined_probs = {}
        for result in ['win', 'draw', 'lose']:
            combined_probs[result] = (
                location_stats[result] * 0.4 +
                opponent_stats[result] * 0.4 +
                self.overall_stats[result] * 0.2
            )

        # Normaliseerimine
        total = sum(combined_probs.values())
        for result in combined_probs:
            combined_probs[result] /= total

        # Kõige tõenäolisema tulemuse valimine
        prediction = max(combined_probs.items(), key=lambda x: x[1])

        return {
            'prediction': prediction[0],
            'probabilities': combined_probs,
            'confidence': prediction[1]
        }


# ===== Mudeli treenimine =====
model = SimpleBVBModel()
model.fit(bvb_matches)

print("\nMUDELI TREENIMINE")
print("Üldstatistika:")
for result, prob in model.overall_stats.items():
    print(f"  {result}: {prob:.2%}")

print("\nStatistika asukoha järgi:")
for location in ['home', 'away']:
    print(f"  {location}:")
    for result, prob in model.stats[location].items():
        print(f"    {result}: {prob:.2%}")


# ===== Ennustuste testimine =====
print("\nENNUSTUSED")

def predict_and_display(opponent, is_home=True):
    """
    Abifunktsioon ennustuse kuvamiseks
    """
    result = model.predict(opponent, is_home)
    print(f"\nBorussia Dortmund vs {opponent}")
    print(f"Asukoht: {'Kodus' if is_home else 'Võõrsil'}")
    print(f"Ennustus: {result['prediction'].upper()}")
    print(f"Usaldus: {result['confidence']:.2%}")
    print("Tõenäosused:")
    for res, prob in result['probabilities'].items():
        print(f"  {res}: {prob:.2%}")


# Testandmed
test_matches = [
    ("Bayern Munich", False),
    ("Mainz", True),
    ("RB Leipzig", False),
    ("Köln", True),
    ("Bayer Leverkusen", True)
]

for opponent, is_home in test_matches:
    predict_and_display(opponent, is_home)


# ===== Mudeli täpsuse analüüs =====
print("\nTulemuslikkuse analüüs")

def calculate_accuracy(model, data):
    """
    Arvutab mudeli täpsuse võrreldes tegelike tulemustega
    """
    correct = 0
    total = len(data)

    for _, match in data.iterrows():
        if 'Borussia Dortmund' in str(match['Home Team']):
            opponent = str(match['Away Team'])
            is_home = True
        else:
            opponent = str(match['Home Team'])
            is_home = False

        prediction = model.predict(opponent, is_home)['prediction']
        actual = match['BVB_Result']

        if prediction == actual:
            correct += 1

    return correct / total


accuracy = calculate_accuracy(model, bvb_matches)
print(f"Andmete põhjal täpsus: {accuracy:.2%}")


# ===== Viimaste mängude kuvamine =====
print("\nStatistika")
print("Viimased 10 mängu:")

recent_matches = bvb_matches.tail(10)[['Home Team', 'Away Team', 'Result', 'BVB_Result']]
print(recent_matches.to_string(index=False))
