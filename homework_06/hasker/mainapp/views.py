from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, DetailView, ListView, View
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import UserBase, Question, Tags, Reply
from .forms import RegisterForm, UserLoginForm, UserUpdateForm, QuestionCreateForm


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
    
    def get_success_url(self):
        return f'/settings/{self.request.user.id}'

class QuestionCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Question
    form_class = QuestionCreateForm
    template_name = 'mainapp/question_create.html'
    login_url = '/login/'
    success_message = 'Your question has been successfully created'

    def get_success_url(self):
        return '/'

class QuetionDetailView(DetailView):
    model = Question
    template_name = 'mainapp/question_detail.html'
    

