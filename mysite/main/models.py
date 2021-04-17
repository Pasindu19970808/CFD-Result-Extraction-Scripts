from django.db import models
from datetime import datetime

# Create your models here.
#inherit from the model.Model class
class Tutorial(models.Model):
    #what this does is create a new Table called Tutorial in the SQLITE3 database and puts these as the columns of your table
    tutorial_title = models.CharField(max_length = 200)
    tutorial_content = models.TextField()
    tutorial_published = models.DateTimeField(default=datetime.now())