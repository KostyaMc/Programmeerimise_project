from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),       # main page
    path('about/', views.about, name='about'),  # about page
    path('squad/', views.squad, name='squad')
]