from django.db import models

# calculating percentages
class Club(models.Model):
    name = models.CharField(max_length=100)
    games = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)

    def win_percentage(self):
        return round(self.wins / self.games * 100, 1) if self.games else 0
    
    def draw_percentage(self):
        return round(self.draws / self.games * 100, 1) if self.games else 0   
    
    def loss_percentage(self):
        return round(self.losses / self.games * 100, 1) if self.games else 0

