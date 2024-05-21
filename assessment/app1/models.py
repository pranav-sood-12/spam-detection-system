from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class User_Profile(models.Model):
    username=models.CharField(max_length=50, null=True)
    phone_number=models.IntegerField(null=False, unique=True)
    email=models.EmailField(max_length=50, null=True)
    password = models.CharField(max_length=128,null=True) 
    spam = models.BooleanField(default=False)
    def __str__(self):
        return str(self.username)

from .models import User_Profile

class Contacts(models.Model):
    user_profile = models.ForeignKey(User_Profile, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50, null=False)
    phone_number = models.IntegerField(null=False)
    email = models.EmailField(null=True)
    spam = models.BooleanField(default=False)

    def __str__(self):
        return self.name
