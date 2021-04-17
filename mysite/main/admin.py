from django.contrib import admin
from .models import Tutorial
from tinymce.widgets import TinyMCE
from django.db import models
# Register your models here.

class TutorialAdmin(admin.ModelAdmin):
    #This will give a basic view
    """ fields = ["tutorial_title",
                "tutorial_content",
                "tutorial_published"] """
    #For us to separate it out nicely, we can do as follows:
    fieldsets = [("Title",{"fields":["tutorial_title"]}),
                 ("Content",{"fields":["tutorial_content"]}),
                 ("Date",{"fields":["tutorial_published"]})
    ]

    formfield_overrides = {
        models.TextField: {'widget':TinyMCE()}
    }






admin.site.register(Tutorial, TutorialAdmin)