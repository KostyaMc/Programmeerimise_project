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
    return HttpResponse("About us")