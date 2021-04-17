from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

#creating the call for a view(equivalent to calling a view from the View folder in ASP.NET Core)
def homepage(request):
    return HttpResponse("<div> HI </div>")