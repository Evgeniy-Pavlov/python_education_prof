from django.contrib import admin
from .models import UserBase, Question, Tags, Reply

# Register your models here.
@admin.register(UserBase)
class AdminUser(admin.ModelAdmin):
    list_display = ('id', 'username', 'logo', 'date_create', 'email', 'password')

@admin.register(Tags)
class AdminTags(admin.ModelAdmin):
    list_display = ('tag',)

@admin.register(Question)
class AdminQuesttion(admin.ModelAdmin):
    list_display = ('header', 'body', 'user_create', 'date_create')

@admin.register(Reply)
class AdminReply(admin.ModelAdmin):
    list_display = ('text', 'user_create', 'best_reply')
