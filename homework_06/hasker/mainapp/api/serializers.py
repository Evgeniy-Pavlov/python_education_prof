from rest_framework.serializers import ModelSerializer, CharField, DateTimeField, IntegerField, Field, ListField
from mainapp.models import Question, UserBase, MTMQuestionRating, Tags, Reply, MTMReplyRating

class QuestionsSerializer(ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'header', 'body', 'date_create', 'user_create')

class QuestionSerializer(ModelSerializer):
    username = CharField(source='user_create.username')
    votes = IntegerField()

    class Meta:
        model = Question
        fields = ('id', 'header', 'body', 'date_create', 'user_create', 'username', 'votes', 'tags')

class SearchQuestionsSerializer(ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'header', 'body', 'date_create', 'user_create')

class ReplySerializer(ModelSerializer):
    question_header = CharField(source='question.header')
    
    class Meta:
        model = Reply
        fields = ('id', 'text', 'user_create', 'best_reply', 'date_create', 'question', 'question_header')