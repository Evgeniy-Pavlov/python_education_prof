from django.db.models import Q, Count, Case, When
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import QuestionsSerializer, QuestionSerializer
from mainapp.models import UserBase, Question, Tags, Reply, MTMQuestionRating, MTMReplyRating

class BasePageAPIView(ListAPIView):
    """Получение списка вопросов. Имеет только 1 query-параметр sort. При передаче значения sort='votes'
    сортирует по голосам, при иных значениях параметра сортирует по дате создания."""
    serializer_class = QuestionsSerializer

    def get(self, request):
        sort_param = '-votes' if request.query_params['sort'] == 'votes' else '-date_create'
        result =Question.objects.all().values('id', 'header', 'body', 'user_create__id', 'user_create__username', 'date_create')\
                .annotate(votes= Count(Case(When(mtmquestionrating__is_positive=True, then=1)))-\
                Count(Case(When(mtmquestionrating__is_positive=False, then=1)))).order_by(sort_param)
        for question in result:
            tags_get = Question.objects.filter(id = question.get('id')).values('tags__id', 'tags__tag')
            if tags_get[0]['tags__id']:
                question['tags_list'] = tags_get
        return Response(result)

class QuestionAPIView(APIView):
    serializer_class = QuestionSerializer

    def get(self, request, pk):
        result = Question.objects.filter(id=pk).annotate(votes= Count(Case(When(mtmquestionrating__is_positive=True, mtmquestionrating__question_rated= int(pk), then=1)))-\
                Count(Case(When(mtmquestionrating__is_positive=False, mtmquestionrating__question_rated= int(pk), then=1)))).order_by('id')
        return Response(QuestionSerializer(result, many=True).data)

        
