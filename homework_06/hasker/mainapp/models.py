from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

# Create your models here.
class UserBase(AbstractUser):
    """Базовая модель пользователя."""
    username = models.CharField(unique=True, max_length=40)
    logo = models.ImageField(upload_to='userbase', blank=True, null=True)
    date_create = models.DateTimeField(default=datetime.now)
    email = models.EmailField(unique=True)

    class Meta:
        verbose_name_plural = 'UserBase'

class Tags(models.Model):
    """Модель тэгов."""
    tag = models.CharField(unique= True, max_length=30)

    class Meta:
        verbose_name_plural = 'Tags'

class Question(models.Model):
    """Модель вопросов. Имеет many-to-many связь с таблицей Tags."""
    header = models.CharField(max_length=100)
    body = models.TextField(max_length=2000)
    user_create = models.ForeignKey(UserBase, on_delete=models.SET_NULL, null=True)
    date_create = models.DateTimeField(default=datetime.now)
    tags = models.ManyToManyField(Tags)

    class Meta:
        verbose_name_plural = 'Question'

class Reply(models.Model):
    """Модель ответов на вопросы. Имеет внешний ключ указывающий на таблицу Question."""
    text = models.TextField(max_length=500)
    user_create = models.ForeignKey(UserBase, on_delete=models.SET_NULL, null=True)
    best_reply = models.BooleanField(default=False)
    date_create = models.DateTimeField(default=datetime.now)
    question = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = 'Reply'

class MTMQuestionRating(models.Model):
    """Модель many-to-many связи оценки вопроса пользователем."""
    user_rated = models.ForeignKey(UserBase, on_delete=models.CASCADE, unique=False)
    question_rated = models.ForeignKey(Question, on_delete=models.CASCADE, unique=False)
    is_positive = models.BooleanField(default=False)

class MTMReplyRating(models.Model):
    """Модель many-to-many связи оценки ответа пользователем."""
    user_rated = models.ForeignKey(UserBase, on_delete=models.CASCADE, unique=False)
    reply_rated = models.ForeignKey(Reply, on_delete=models.CASCADE, unique=False)
    is_positive = models.BooleanField(default=False)
