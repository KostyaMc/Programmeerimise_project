from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def club(request):
    return HttpResponse("BVB club")