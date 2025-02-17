from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    class Jobchoices(models.TextChoices):
        NETWORK = ("network", "Network")
        SYSTEM = ("system", "System")
        DB = ("database", "Database")
        APP = ("webapp", "WEBAPP")
        QUALITY = ("quality", "Quality")

    first_name = models.CharField(max_length=150, editable=False)
    last_name = models.CharField(max_length=150, editable=False)
    name = models.CharField(max_length=150)
    job = models.CharField(max_length=50, choices=Jobchoices.choices,)
    
    def __str__(self) -> str:
        return self.name
