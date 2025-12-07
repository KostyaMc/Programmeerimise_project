import pandas as pd
import numpy as np
from collections import Counter
import random
import os


# Загрузка данных
#data = pd.read_csv('bvb-2024.csv', encoding='cp1251', delimiter=',')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(BASE_DIR, 'data', 'bvb-2024.csv')
data = pd.read_csv(csv_path, encoding='cp1251', delimiter=',')

print("Первые строки данных:")
print(data.head())

# 1. Создаем целевую переменную
def get_match_result(row):
    """
    Определяем результат матча для Боруссии Дортмунд
    """
    home_team = str(row['Home Team'])
    away_team = str(row['Away Team'])
    
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

# Применяем функцию
data['BVB_Result'] = data.apply(get_match_result, axis=1)
bvb_matches = data[data['BVB_Result'].notna()].copy()

print(f"\nВсего матчей Боруссии: {len(bvb_matches)}")
print("Распределение результатов:")
print(bvb_matches['BVB_Result'].value_counts())

# 2. Простая модель на основе статистики
class SimpleBVBModel:
    def __init__(self):
        self.stats = {}
        self.overall_stats = {}
    
    def fit(self, data):
        """Обучаем модель на исторических данных"""
        # Общая статистика
        self.overall_stats = dict(data['BVB_Result'].value_counts())
        total_matches = len(data)
        for result in self.overall_stats:
            self.overall_stats[result] /= total_matches
        
        # Статистика по домашним/гостевым
        home_stats = data[data['Home Team'].str.contains('Borussia Dortmund')]['BVB_Result'].value_counts()
        away_stats = data[data['Away Team'].str.contains('Borussia Dortmund')]['BVB_Result'].value_counts()
        
        self.stats['home'] = {}
        self.stats['away'] = {}
        
        for result in ['win', 'draw', 'lose']:
            self.stats['home'][result] = home_stats.get(result, 0) / len(home_stats) if len(home_stats) > 0 else 0
            self.stats['away'][result] = away_stats.get(result, 0) / len(away_stats) if len(away_stats) > 0 else 0
        
        # Статистика по силе соперников
        strong_teams = ['Bayern', 'Leipzig', 'Leverkusen', 'Stuttgart', 'Frankfurt']
        medium_teams = ['Wolfsburg', 'Gladbach', 'Hoffenheim', 'Augsburg', 'Freiburg']
        
        self.stats['vs_strong'] = self._calculate_opponent_stats(data, strong_teams)
        self.stats['vs_medium'] = self._calculate_opponent_stats(data, medium_teams)
        self.stats['vs_weak'] = self._calculate_opponent_stats(data, [], exclude=strong_teams + medium_teams)
        
        return self
    
    def _calculate_opponent_stats(self, data, team_list, exclude=None):
        """Рассчитываем статистику против определенных команд"""
        if exclude is None:
            exclude = []
        
        opponent_matches = []
        for _, row in data.iterrows():
            if 'Borussia Dortmund' in str(row['Home Team']):
                opponent = str(row['Away Team'])
            else:
                opponent = str(row['Home Team'])
            
            if team_list:
                # Если указан список команд, берем только их
                if any(team in opponent for team in team_list):
                    opponent_matches.append(row['BVB_Result'])
            else:
                # Иначе берем всех, кроме исключенных
                if not any(excl_team in opponent for excl_team in exclude):
                    opponent_matches.append(row['BVB_Result'])
        
        if not opponent_matches:
            return {'win': 0.33, 'draw': 0.33, 'lose': 0.34}
        
        stats = Counter(opponent_matches)
        total = len(opponent_matches)
        return {result: stats.get(result, 0) / total for result in ['win', 'draw', 'lose']}
    
    def predict(self, opponent, is_home=True):
        """Предсказываем результат матча"""
        # Определяем силу соперника
        strong_teams = ['Bayern', 'Leipzig', 'Leverkusen', 'Stuttgart', 'Frankfurt']
        medium_teams = ['Wolfsburg', 'Gladbach', 'Hoffenheim', 'Augsburg', 'Freiburg']
        
        if any(team in opponent for team in strong_teams):
            opponent_stats = self.stats['vs_strong']
        elif any(team in opponent for team in medium_teams):
            opponent_stats = self.stats['vs_medium']
        else:
            opponent_stats = self.stats['vs_weak']
        
        # Комбинируем статистику
        location_stats = self.stats['home' if is_home else 'away']
        
        # Среднее взвешенное (можно настроить веса)
        combined_probs = {}
        for result in ['win', 'draw', 'lose']:
            combined_probs[result] = (location_stats[result] * 0.4 + 
                                    opponent_stats[result] * 0.4 + 
                                    self.overall_stats[result] * 0.2)
        
        # Нормализуем вероятности
        total = sum(combined_probs.values())
        for result in combined_probs:
            combined_probs[result] /= total
        
        # Выбираем наиболее вероятный результат
        prediction = max(combined_probs.items(), key=lambda x: x[1])
        
        return {
            'prediction': prediction[0],
            'probabilities': combined_probs,
            'confidence': prediction[1]
        }

model = SimpleBVBModel()
model.fit(bvb_matches)

# 3. Обучаем модель
print("\n=== ОБУЧЕНИЕ МОДЕЛИ ===")
model = SimpleBVBModel()
model.fit(bvb_matches)

print("Общая статистика:")
for result, prob in model.overall_stats.items():
    print(f"  {result}: {prob:.2%}")

print("\nСтатистика по месту:")
for location in ['home', 'away']:
    print(f"  {location}:")
    for result, prob in model.stats[location].items():
        print(f"    {result}: {prob:.2%}")

# 4. Делаем предсказания
print("\n=== ПРЕДСКАЗАНИЯ ===")

def predict_and_display(opponent, is_home=True):
    result = model.predict(opponent, is_home)
    print(f"\nБоруссия Дортмунд vs {opponent}")
    print(f"Место: {'Дома' if is_home else 'В гостях'}")
    print(f"Предсказание: {result['prediction'].upper()}")
    print(f"Уверенность: {result['confidence']:.2%}")
    print("Вероятности:")
    for res, prob in result['probabilities'].items():
        print(f"  {res}: {prob:.2%}")

# Тестовые предсказания
test_matches = [
    ("Bayern Munich", False),
    ("Mainz", True),
    ("RB Leipzig", False),
    ("Köln", True),
    ("Bayer Leverkusen", True)
]

for opponent, is_home in test_matches:
    predict_and_display(opponent, is_home)

# 5. Анализ эффективности модели
print("\n=== АНАЛИЗ ЭФФЕКТИВНОСТИ ===")

def calculate_accuracy(model, data):
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
print(f"Точность на исторических данных: {accuracy:.2%}")

# 6. Простая визуализация
print("\n=== СТАТИСТИКА ===")
print("Последние 10 матчей Боруссии:")
recent_matches = bvb_matches.tail(10)[['Home Team', 'Away Team', 'Result', 'BVB_Result']]
print(recent_matches.to_string(index=False))
