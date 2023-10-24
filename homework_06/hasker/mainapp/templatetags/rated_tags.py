from django import template
from mainapp.models import MTMQuestionRating, Question, UserBase

register = template.Library()

@register.simple_tag(takes_context=True)
def question_rated(context):
    result = MTMQuestionRating.objects.filter(question_rated=Question.objects.get(id=context['question'].id), user_rated=context['user'])
    return (False, False) if not result else (result, result[0].is_positive)