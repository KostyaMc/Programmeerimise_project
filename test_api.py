import requests

url = "https://api.football-data.org/v4/matches"
headers = {"X-Auth-Token": "0969f3f7693f4b7a9803059c33490f65"}

response = requests.get(url, headers=headers)
print(response.status_code)
print(response.json())