from django.shortcuts import render
#from django.http import HttpResponse
#import os
# Create your views here.

posts = [
    {
        'author': 'Pasindu S', 
        'title': 'Blog Post 1', 
        'content': 'First Post Content', 
        'date_posted': 'August 27, 2021'
    }, 
    {
        'author': 'J Doe', 
        'title': 'Blog Post 2', 
        'content': 'Second Post Content', 
        'date_posted': 'August 28, 2021'
    }

]





#This function will handle the traffic from the homepage of our blog
def home(request):
    """ #Reading an html using path, and then presenting it as HttpResponse(Tedious method)
    current_filepath = os.path.abspath(os.getcwd())
    html_path = os.path.join(current_filepath,"blog","templates","blog","home.html")
    html_content = open(html_path,'r')
    #return HttpResponse("<h1>" + html_path + "</h1>")
    return HttpResponse(html_content) """

    #context is the dictionary we pass through the render function to the html
    #to this we can add more key pair values
    context = {
        'posts':posts
    }

    return render(request, template_name = 'blog/home.html', context = context)

def about(request):
    context = {
        'title':'About'
    }
    return render(request, template_name = 'blog/about.html', context = context)