from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, DetailView, ListView, View, FormView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from .models import UserBase, Question, Tags, Reply
from .forms import RegisterForm


class BasePageView(ListView):
    model = Question
    template_name = 'mainapp/base_page.html'

class RegisterView(CreateView):
    model = UserBase
    form_class = RegisterForm
    success_url = '/'
    template_name = 'mainapp/registration_user.html'