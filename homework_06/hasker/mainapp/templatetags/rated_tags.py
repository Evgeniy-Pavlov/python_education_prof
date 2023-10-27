from django import template
from django.db.models import Case, Value, When, Sum
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
    """select mm.question_rated_id , (sum(case when mm.is_positive then 1 else 0 end) - sum(case when is_positive then 0 else 1 end)) as rated
        from mainapp_mtmquestionrating mm 
        group by mm.question_rated_id 
        order by rated desc
        LIMIT 20"""
    result = MTMQuestionRating.objects.annotate(rating = Sum(Case(When(is_positive=True, then=1)))\
         - Sum(Case(When(is_positive=False, then=1)))).values('rating', 'question_rated').order_by('rating')
    print(result)
    return result