from django.db import models
from django.contrib.auth.models import User

class SSHPublicKey(models.Model):
    user = models.ForeignKey(User) 
    key = models.TextField()

class SimplePermission(models.Model):
    user = models.ForeignKey(User)
    permission_string = models.CharField(max_length=255)

