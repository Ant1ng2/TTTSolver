from django.shortcuts import render
from django.http import HttpResponse

def play(request):
    return render(request, 'tic/play.html')
