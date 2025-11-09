from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request) -> HttpResponse:
    context = {
        'title': 'Home',
        'content': 'Team home page'
    }

    return render(request, 'main/index.html', context)


def about(request):
    context = {
        'title': 'About us',
        'content': 'This page contains basic information about the sites creators',
        'text_on_page': 'НАДО ПРИДУМАТЬ И ДОБАВИТЬ'
    }

    return render(request, 'main/about.html', context)