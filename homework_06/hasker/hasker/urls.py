"""
URL configuration for hasker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from mainapp.views import BasePageView, RegisterView, UserLoginView, UserLogoutView, UserProfileView, QuestionCreateView, QuetionDetailView, ReplyCreateView, \
    QuestionRatedUpView, QuestionRatedDownView, QuestionRatedCancelView, ReplyRatedUpView, ReplyRatedDownView, ReplyRatedCancelView, BestReplySetView, SearchQuestionView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', BasePageView.as_view()),
    path('signup/', RegisterView.as_view()),
    path('login/', UserLoginView.as_view()),
    path('logout/', UserLogoutView.as_view()),
    path('settings/<int:pk>', UserProfileView.as_view()),
    path('ask/', QuestionCreateView.as_view()),
    path('question/<int:pk>', QuetionDetailView.as_view()),
    path('reply-create/<int:pk>', ReplyCreateView.as_view()),
    path('question-up/<int:pk>', QuestionRatedUpView.as_view()),
    path('question-down/<int:pk>', QuestionRatedDownView.as_view()),
    path('question-cancel/<int:pk>', QuestionRatedCancelView.as_view()),
    path('reply-up/<int:question>/<int:pk>', ReplyRatedUpView.as_view()),
    path('reply-down/<int:question>/<int:pk>', ReplyRatedDownView.as_view()),
    path('reply-cancel/<int:question>/<int:pk>', ReplyRatedCancelView.as_view()),
    path('reply-best/<int:question>/<int:pk>', BestReplySetView.as_view()),
    path('search/', SearchQuestionView.as_view()),
    path('__debug__/', include('debug_toolbar.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
