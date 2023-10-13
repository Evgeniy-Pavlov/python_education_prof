from django.contrib import admin
from .models import Question, Choice

# Register your models here.
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


@admin.register(Question)
class AdminQuestion(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['question_text']}),\
        ('Date information', {'fields': ['pub_date']})]
    inlines = [ChoiceInline]
    list_display = ('id', 'question_text', 'pub_date')

@admin.register(Choice)
class AdminChoice(admin.ModelAdmin):
    list_display = ('id', 'question', 'choice_text', 'votes')
