from http import HTTPStatus
from django.db.models import Q, Count, Case, When
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import QuestionsSerializer, QuestionSerializer, SearchQuestionsSerializer, ReplySerializer, MyQueryParamSerializer
from mainapp.models import UserBase, Question, Tags, Reply, MTMQuestionRating, MTMReplyRating
from .paginators import MyPagination
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

class BasePageAPIView(ListAPIView):
    """Получение списка вопросов. Метод имеет пагинацию по 20 вопросов на страницу."""
    serializer_class = QuestionsSerializer
    queryset = Question.objects.all().values('id', 'header', 'body', 'date_create', 'user_create__id', 'user_create__username')\
                .annotate(votes= Count(Case(When(mtmquestionrating__is_positive=True, then=1)))-\
                Count(Case(When(mtmquestionrating__is_positive=False, then=1)))).order_by('-votes')
    pagination_class = MyPagination


class QuestionAPIView(APIView):
    """Метод получения информации об вопросе. Id вопроса передается прямо в урле
    в формате question/{id вопроса}."""
    serializer_class = QuestionSerializer

    def get(self, request, pk):
        result = Question.objects.filter(id=pk).annotate(votes= Count(Case(When(mtmquestionrating__is_positive=True, mtmquestionrating__question_rated= int(pk), then=1)))-\
                Count(Case(When(mtmquestionrating__is_positive=False, mtmquestionrating__question_rated= int(pk), then=1))))
        return Response(QuestionSerializer(result, many=True).data[0]) if len(QuestionSerializer(result, many=True)\
            .data) else Response({"error": "Question not found."}, status=HTTPStatus.NOT_FOUND)

class SearchAPIView(APIView):
    """Метод поиска по названию, описанию и связанному тэгу вопросов.
    Правила указания поискового запроса.
    Поиск принимает только один из двух квери-параметров:
    1. strng - В поле может быть указано часть текста из описания или названия
    2. tag - Может быть осуществлен поиск по тэгу.
    Возвращает список вопросов подходящих под условия поиска, отсортированные по популярности."""
    serializer_class = SearchQuestionsSerializer

    @swagger_auto_schema(query_serializer=MyQueryParamSerializer, 
                            manual_parameters=[openapi.Parameter(name='strng', in_=openapi.IN_QUERY,
                            description='Substring header question or body',
                            type=openapi.TYPE_STRING,
                            required=False), openapi.Parameter(name='tag', in_=openapi.IN_QUERY,
                            description='Tag related question',
                            type=openapi.TYPE_STRING,
                            required=False)])
    def get(self, request):
        if 'strng' in request.query_params.keys():
            search_request = request.query_params['strng']
            result = Question.objects.filter(Q(header__icontains = search_request) | Q(body__icontains = search_request))\
                .values('id', 'header', 'body', 'user_create', 'user_create__logo', 'user_create__username', 'date_create')\
                .annotate(votes= Count(Case(When(mtmquestionrating__is_positive=True, then=1)))-\
                Count(Case(When(mtmquestionrating__is_positive=False, then=1)))).order_by('-votes')
        elif 'tag' in request.query_params.keys():
            search_request = request.query_params['tag']
            result = Question.objects.filter(tags__tag=search_request).values('id', 'header', 'body',\
                'user_create__logo', 'user_create__username', 'date_create')\
                .annotate(votes= Count(Case(When(mtmquestionrating__is_positive=True, then=1)))-\
                Count(Case(When(mtmquestionrating__is_positive=False, then=1)))).order_by('-votes')
        return Response(SearchQuestionsSerializer(result, many=True).data)

class ReplyAPIView(APIView):
    """Метод получения ответов созданных на указанный вопрос.
    Id вопроса передается прямо урле в формате question/{id вопроса}/reply."""
    serializer_class = ReplySerializer
    
    def get(self, request, pk):
        try:
            Question.objects.get(id=pk)
        except Question.DoesNotExist:
            return Response({"error": "Question not found."}, status=404)
        result = Reply.objects.filter(question=Question.objects.get(id=pk)).select_related('mtmreplyrating__reply_rated')\
        .values('id', 'text', 'best_reply', 'user_create_id', 'question_id', 'date_create','user_create_id__username')\
        .annotate(rating= Count(Case(When(mtmreplyrating__is_positive=True, then=1)))\
        - Count(Case(When(mtmreplyrating__is_positive=False, then=1)))).order_by('rating', 'date_create')[::-1]
        return Response(ReplySerializer(result, many=True).data)

class TrendingAPIView(ListAPIView):
    """Метод возвращает топ-20 самых популярных вопросов по рейтингу."""
    serializer_class = QuestionsSerializer
    queryset = Question.objects.all().values('id', 'header', 'body', 'date_create', 'user_create__id', 'user_create__username')\
                .annotate(votes= Count(Case(When(mtmquestionrating__is_positive=True, then=1)))-\
                Count(Case(When(mtmquestionrating__is_positive=False, then=1)))).order_by('-votes')[:20]
        

        
