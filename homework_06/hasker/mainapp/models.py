from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

# Create your models here.
class UserBase(AbstractUser):
    username = models.CharField(unique=True, max_length=40)
    logo = models.ImageField(upload_to='userbase', blank=True, null=True)
    date_create = models.DateTimeField(default=datetime.now)
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name_plural = 'UserBase'

class Tags(models.Model):
    tag = models.CharField(unique= True, max_length=30)

    class Meta:
        verbose_name_plural = 'Tags'

class Question(models.Model):
    header = models.CharField(max_length=100)
    body = models.TextField(max_length=2000)
    user_create = models.ForeignKey(UserBase, on_delete=models.SET_NULL, null=True)
    date_create = models.DateTimeField(default=datetime.now)

    class Meta:
        verbose_name_plural = 'Question'

class Reply(models.Model):
    text = models.TextField(max_length=500)
    user_create = models.ForeignKey(UserBase, on_delete=models.SET_NULL, null=True)
    best_reply = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Reply'



