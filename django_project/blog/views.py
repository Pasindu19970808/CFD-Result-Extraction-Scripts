from django.shortcuts import render
#from django.http import HttpResponse
import os
# Create your views here.

#This function will handle the traffic from the homepage of our blog
def home(request):
    """ #Reading an html using path, and then presenting it as HttpResponse(Tedious method)
    current_filepath = os.path.abspath(os.getcwd())
    html_path = os.path.join(current_filepath,"blog","templates","blog","home.html")
    html_content = open(html_path,'r')
    #return HttpResponse("<h1>" + html_path + "</h1>")
    return HttpResponse(html_content) """
    return render(request, template_name = 'blog/home.html')

def about(request):
    return render(request, template_name = 'blog/about.html')