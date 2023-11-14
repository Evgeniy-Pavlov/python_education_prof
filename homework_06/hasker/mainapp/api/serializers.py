from rest_framework.serializers import ModelSerializer, CharField, DateTimeField, IntegerField, Field, ListField
from mainapp.models import Question, UserBase, MTMQuestionRating, Tags, Reply, MTMReplyRating

class QuestionsSerializer(ModelSerializer):
    user_create = IntegerField(source='user_create__id')
    username = CharField(source='user_create__username')
    votes = IntegerField()

    class Meta:
        model = Question
        fields = ('id', 'header', 'body', 'date_create', 'user_create', 'username', 'votes')

class QuestionSerializer(ModelSerializer):
    username = CharField(source='user_create.username')
    votes = IntegerField()

    class Meta:
        model = Question
        fields = ('id', 'header', 'body', 'date_create', 'user_create', 'username', 'votes', 'tags')

class SearchQuestionsSerializer(ModelSerializer):
    logo = CharField(source='user_create__logo')
    username = CharField(source='user_create__username')

    class Meta:
        model = Question
        fields = ('id', 'header', 'body',  'logo', 'username', 'date_create' )

class ReplySerializer(ModelSerializer):
    user_create = IntegerField(source='user_create_id')
    username = CharField(source='user_create_id__username')
    rating = IntegerField()
    
    class Meta:
        model = Reply
        fields = ('id', 'text', 'best_reply', 'user_create', 'question_id', 'date_create', 'username', 'rating')

class MyQueryParamSerializer(ModelSerializer):
    strng = CharField(help_text='Substring header question or body', required=False)
    tag = CharField(help_text='Tag related question', required=False)

    class Meta:
        model = Question
        fields = ('strng', 'tag')
