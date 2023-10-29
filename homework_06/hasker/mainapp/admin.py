from django.contrib import admin
from .models import UserBase, Question, Tags, Reply, MTMQuestionRating, MTMReplyRating

# Register your models here.
@admin.register(UserBase)
class AdminUser(admin.ModelAdmin):
    list_display = ('id', 'username', 'logo', 'date_create', 'email', 'password')

@admin.register(Tags)
class AdminTags(admin.ModelAdmin):
    list_display = ('tag',)

@admin.register(Question)
class AdminQuesttion(admin.ModelAdmin):
    def group_tags(self, question):
        return ','.join([x.tag for x in question.tags.all()])

    list_display = ('header', 'body', 'user_create', 'date_create', 'group_tags')

@admin.register(Reply)
class AdminReply(admin.ModelAdmin):
    list_display = ('text', 'user_create', 'best_reply', 'date_create', 'question')

@admin.register(MTMQuestionRating)
class AdminMTMQuestionRating(admin.ModelAdmin):
    list_display = ('user_rated', 'question_rated', 'is_positive')

@admin.register(MTMReplyRating)
class AdminMTMReplyRating(admin.ModelAdmin):
    list_display = ('user_rated', 'reply_rated', 'is_positive')
