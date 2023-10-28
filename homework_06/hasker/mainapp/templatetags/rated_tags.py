from django import template
from django.db.models import Case, Value, When, Sum, Count
from mainapp.models import MTMQuestionRating, Question, UserBase, MTMReplyRating, Reply

register = template.Library()

@register.simple_tag(takes_context=True)
def question_rated(context):
    result = MTMQuestionRating.objects.filter(question_rated=Question.objects.get(id=context['question'].id), user_rated=context['user'])
    return bool(result)

@register.simple_tag(takes_context=True)
def question_counter_rated(context):
    result = len(MTMQuestionRating.objects.filter(question_rated=Question.objects.get(id=context['question'].id), is_positive=True)) - \
        len(MTMQuestionRating.objects.filter(question_rated=Question.objects.get(id=context['question'].id), is_positive=False))
    return result

@register.simple_tag(takes_context=True)
def reply_rated(context):
    result = MTMReplyRating.objects.filter(reply_rated=Reply.objects.get(id=context['reply'].id), user_rated=context['user'])
    return bool(result)

@register.simple_tag(takes_context=True)
def reply_counter_rated(context):
    result = len(MTMReplyRating.objects.filter(reply_rated=Reply.objects.get(id=context['reply'].id), is_positive=True))  - \
        len(MTMReplyRating.objects.filter(reply_rated=Reply.objects.get(id=context['reply'].id),is_positive=False))
    return result

@register.simple_tag(takes_context=True)
def question_treding(context):
    result = MTMQuestionRating.objects.all().select_related('question__id').values('question_rated_id', 'question_rated_id__header').annotate(rating = Count(Case(When(is_positive=True, then=1)))\
         - Count(Case(When(is_positive=False, then=1)))).order_by('rating')[:20:-1]
    return result