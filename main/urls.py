from django.urls import path
from . import views

# URL-mustrite loend rakenduse jaoks
urlpatterns = [

    # Avalehe URL
    # Suunab juuraadressilt "/" funktsiooni index views.py failis
    path('', views.index, name='home'),

    # "Meist" lehe URL
    # Kuvab info projekti ja autorite kohta
    path('about/', views.about, name='about'),

    # "Meeskond" lehe URL
    # Kuvab Borussia Dortmundi mängijate koosseisu
    path('squad/', views.squad, name='squad'),
]
