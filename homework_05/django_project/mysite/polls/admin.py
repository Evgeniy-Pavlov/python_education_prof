from django.contrib import admin
from .models import Question, Choice

# Register your models here.

@admin.register(Question)
class AdminQuestion(admin.ModelAdmin):
    list_display = ('id', 'question_text', 'pub_date')

@admin.register(Choice)
class AdminChoice(admin.ModelAdmin):
    list_display = ('id', 'question', 'choice_text', 'votes')