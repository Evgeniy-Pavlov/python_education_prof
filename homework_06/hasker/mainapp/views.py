from django.db.models import Q, Count, Case, When
from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, DetailView, ListView, View
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import UserBase, Question, Tags, Reply, MTMQuestionRating, MTMReplyRating
from .forms import RegisterForm, UserLoginForm, UserUpdateForm, QuestionCreateForm, ReplyCreateForm, RatedQuestionForm, RatedReplyForm, BestReplyForm


class BasePageView(ListView):
    model = Question
    template_name = 'mainapp/base_page.html'
    paginate_by = 20

    def get_queryset(self):
        result = Question.objects.all().values('id', 'header', 'user_create__logo', 'user_create__username', 'date_create')\
            .annotate(votes= Count(Case(When(mtmquestionrating__is_positive=True, then=1)))-\
            Count(Case(When(mtmquestionrating__is_positive=False, then=1)))).order_by('-date_create')
        return result

class BasePageHotView(ListView):
    model = Question
    template_name = 'mainapp/base_page_hot.html'
    paginate_by = 20

    def get_queryset(self):
        result = Question.objects.all().values('id', 'header', 'user_create__logo', 'user_create__username', 'date_create')\
            .annotate(votes= Count(Case(When(mtmquestionrating__is_positive=True, then=1)))-\
            Count(Case(When(mtmquestionrating__is_positive=False, then=1)))).order_by('-votes')
        return result

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

class QuestionRatedUpView(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, pk):
        form = RatedQuestionForm(request.POST)
        form.instance.user_rated = self.request.user
        form.instance.question_rated = Question.objects.get(id = pk)
        form.instance.is_positive = True
        form.save()
        return redirect(f'/question/{pk}')

class QuestionRatedDownView(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, pk):
        form = RatedQuestionForm(request.POST)
        form.instance.user_rated = self.request.user
        form.instance.question_rated = Question.objects.get(id = pk)
        form.instance.is_positive = False
        form.save()
        return redirect(f'/question/{pk}')

class QuestionRatedCancelView(LoginRequiredMixin, View):
    login_url = '/login/'
    form_class = RatedQuestionForm

    def post(self, request, pk):
        MTMQuestionRating.objects.filter(user_rated=self.request.user, question_rated=Question.objects.get(id=pk)).delete()
        return redirect(f'/question/{pk}')

class ReplyRatedUpView(LoginRequiredMixin, View):
    login_url = '/login/'
    form_class = RatedReplyForm

    def post(self, request, question, pk):
        form = RatedReplyForm(request.POST)
        form.instance.user_rated = self.request.user
        form.instance.reply_rated = Reply.objects.get(id=pk)
        form.instance.is_positive = True
        form.save()
        return redirect(f'/question/{question}')

class ReplyRatedDownView(LoginRequiredMixin, View):
    login_url = '/login/'
    form_class = RatedReplyForm

    def post(self, request, question, pk):
        form = RatedReplyForm(request.POST)
        form.instance.user_rated = self.request.user
        form.instance.reply_rated = Reply.objects.get(id=pk)
        form.instance.is_positive = False
        form.save()
        return redirect(f'/question/{question}')

class ReplyRatedCancelView(LoginRequiredMixin, View):
    login_url = '/login/'
    form_class = RatedReplyForm

    def post(self, request, question, pk):
        MTMReplyRating.objects.filter(user_rated=self.request.user, reply_rated=Reply.objects.get(id=pk)).delete()
        return redirect(f'/question/{question}')

class BestReplySetView(LoginRequiredMixin, View):
    login_url = '/login/'
    form_class = BestReplyForm

    def post(self, request, question, pk):
        try:
            find_best_reply = Reply.objects.get(question= Question.objects.get(id=question), best_reply=True)
            if find_best_reply.id == pk:
                find_best_reply.best_reply = False
                find_best_reply.save()
            else:
                find_best_reply.best_reply = False
                find_best_reply.save()
                best_reply = Reply.objects.get(id=pk)
                best_reply.best_reply = True
                best_reply.save()
        except Reply.DoesNotExist:
            best_reply = Reply.objects.get(id=pk)
            best_reply.best_reply = True
            best_reply.save()
        return redirect(f'/question/{question}')

class SearchQuestionView(ListView):
    template_name = 'mainapp/search.html'
    paginate_by = 20

    def get_queryset(self):
        search_request = self.request.GET.get('search')
        if search_request[:4] == 'tag:':
            result = Question.objects.filter(tags__tag=search_request[4:]).values('id', 'header', 'user_create__logo', 'user_create__username', 'date_create')\
                .annotate(votes= Count(Case(When(mtmquestionrating__is_positive=True, then=1)))-\
                Count(Case(When(mtmquestionrating__is_positive=False, then=1)))).order_by('-votes')
        else:
            result = Question.objects.filter(Q(header__icontains = search_request) | Q(body__icontains = search_request))\
                .values('id', 'header', 'user_create__logo', 'user_create__username', 'date_create')\
                .annotate(votes= Count(Case(When(mtmquestionrating__is_positive=True, then=1)))-\
                Count(Case(When(mtmquestionrating__is_positive=False, then=1)))).order_by('-votes')
        return result

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search')
        return context
