from rest_framework.serializers import ModelSerializer
from .models import Question

class QuestionSerializer(ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'header', 'user_create', 'date_create')