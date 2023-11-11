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