from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, DetailView, ListView, View
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import UserBase, Question, Tags, Reply, MTMQuestionRating
from .forms import RegisterForm, UserLoginForm, UserUpdateForm, QuestionCreateForm, ReplyCreateForm, RatedQuestionCancelForm, RatedQuestionDownForm, RatedQuestionUpForm, \
    RatedReplyCancelForm, RatedReplyUpForm, RatedReplyDownForm


class BasePageView(ListView):
    model = Question
    template_name = 'mainapp/base_page.html'

class RegisterView(CreateView):
    model = UserBase
    form_class = RegisterForm
    success_url = '/'
    template_name = 'mainapp/registration_user.html'

class UserLoginView(SuccessMessageMixin, LoginView):
    model = UserBase
    form_class = UserLoginForm
    template_name = 'mainapp/login.html'
    success_url = '/'
    success_message = 'Login completed'

class UserLogoutView(SuccessMessageMixin, LogoutView):
    model = UserBase

class UserProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UserBase
    form_class = UserUpdateForm
    template_name = 'mainapp/user_settings.html'
    login_url = '/login/'
    success_message = 'Profile successfully edited'

    def get(self, request, *args, **kwargs):
        if self.request.user == UserBase.objects.get(id=kwargs.get('pk')):
            self.object = self.get_object()
            return super().get(request, *args, **kwargs)
        else:
            return redirect('/')

    def get_success_url(self):
        return f'/settings/{self.request.user.id}'

class QuestionCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Question
    form_class = QuestionCreateForm
    template_name = 'mainapp/question_create.html'
    login_url = '/login/'
    success_message = 'Your question has been successfully created'
    success_url = '/'

    def form_valid(self, form):
        form.instance.user_create = self.request.user
        return super().form_valid(form)

class QuetionDetailView(DetailView):
    model = Question
    template_name = 'mainapp/question_detail.html'

class ReplyCreateView(LoginRequiredMixin, CreateView):
    login_url = '/login/'

    def post(self, request, pk):
        if request.POST['text']:
            form = ReplyCreateForm(request.POST)
            form.instance.user_create = self.request.user
            form.instance.question = Question.objects.get(id=pk)
            form.save()
            return redirect(f'/question/{pk}')
        else:
            return redirect(f'/question/{pk}')

class QuestionRatedUp(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, pk):
        form = RatedQuestionUpForm(request.POST)
        form.instance.user_rated = self.request.user
        form.instance.question_rated = Question.objects.get(id = pk)
        form.instance.is_positive = True
        form.save()
        return redirect(f'/question/{pk}')

class QuestionRatedDown(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, pk):
        form = RatedQuestionDownForm(request.POST)
        form.instance.user_rated = self.request.user
        form.instance.question_rated = Question.objects.get(id = pk)
        form.instance.is_positive = False
        form.save()
        return redirect(f'/question/{pk}')

class QuestionRatedCancel(LoginRequiredMixin, View):
    login_url = '/login/'
    form_class = RatedQuestionDownForm

    def post(self, request, pk):
        MTMQuestionRating.objects.filter(user_rated=self.request.user, question_rated=Question.objects.get(id=pk)).delete()
        return redirect(f'/question/{pk}')

