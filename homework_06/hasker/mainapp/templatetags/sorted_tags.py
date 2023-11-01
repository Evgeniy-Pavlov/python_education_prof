from django import template
from django.db.models import Case, Value, When, Sum, Count
from mainapp.models import MTMQuestionRating, Question, UserBase, MTMReplyRating, Reply

register = template.Library()

@register.simple_tag(takes_context=True)
def question_treding(context):
    result = MTMQuestionRating.objects.all().select_related('question__id').values('question_rated_id', 'question_rated_id__header')\
        .annotate(rating = Count(Case(When(is_positive=True, then=1)))- Count(Case(When(is_positive=False, then=1)))).order_by('rating')[:20:-1]
    return result

@register.simple_tag(takes_context=True)
def reply_sorted(context):
    result = Reply.objects.filter(question=Question.objects.get(id=context['question'].id)).select_related('mtmreplyrating__reply_rated')\
        .values('id', 'text', 'best_reply', 'user_create_id', 'question_id', 'date_create', 'user_create_id__logo', 'user_create_id__username')\
        .annotate(rating= Count(Case(When(mtmreplyrating__is_positive=True, then=1)))\
        - Count(Case(When(mtmreplyrating__is_positive=False, then=1)))).order_by('rating', 'date_create')[::-1]
    return result

@register.simple_tag(takes_context=True)
def question_hot_sorted(context):
    result = Question.objects.all().values('id', 'header', 'user_create__logo', 'user_create__username', 'date_create')\
        .annotate(votes= Count(Case(When(mtmquestionrating__is_positive=True, then=1)))-\
            Count(Case(When(mtmquestionrating__is_positive=False, then=1)))).order_by('votes')[::-1]
    return result

@register.simple_tag(takes_context=True)
def question_new_sorted(context):
    result = Question.objects.all().values('id', 'header', 'user_create__logo', 'user_create__username', 'date_create')\
        .annotate(votes= Count(Case(When(mtmquestionrating__is_positive=True, then=1)))-\
            Count(Case(When(mtmquestionrating__is_positive=False, then=1)))).order_by('date_create')[::-1]
    return result
