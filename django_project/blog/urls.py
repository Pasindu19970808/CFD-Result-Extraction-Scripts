from django.urls import path
from . import views

urlpatterns = [
    #this is the homepage of the blog
    path('', views.home , name='blog-home'),
    path('about/',views.about, name = 'blog-about'),
]