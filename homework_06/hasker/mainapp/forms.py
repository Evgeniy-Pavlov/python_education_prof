from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
from .models import UserBase, Question, Tags, Reply, MTMQuestionRating, MTMReplyRating
from .widgets import ModifiedClearableFileInput

CHOISES_TAGS = [(x['id'], x['tag']) for x in Tags.objects.all().values('id', 'tag')]

class RegisterForm(UserCreationForm):
    """Форма регистрации. Связана с представлением RegisterView."""
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Login', max_length=40)
    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Email')
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Repeat password')
    logo = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control', 'style': 'width: 500px;'}), required=False, label='Avatar')

    class Meta:
        model = UserBase
        fields = ('username', 'email', 'password1', 'password2', 'logo')
    
class UserLoginForm(AuthenticationForm):
    """Форма авторизации. Связана с представлением UserLoginView."""
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Login')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Password')

    class Meta:
        model = UserBase
        fields = ('username', 'password')

class UserUpdateForm(forms.ModelForm):
    """Форма обновления профиля пользователя. Связана с представлением UserProfileView."""
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Email')
    logo = forms.ImageField(widget=ModifiedClearableFileInput(attrs={'class': 'form-control', 'style': 'width: 500px;'}), required=False, label='Avatar')
    
    class Meta:
        model = UserBase
        fields = ('email', 'logo')

class QuestionCreateForm(forms.ModelForm):
    """Форма создания вопроса. Связана с представлением QuestionCreateView."""
    header = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Title', max_length=200)
    body = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), label='Text', max_length=2000)
    tags = forms.MultipleChoiceField(widget=forms.SelectMultiple(attrs={'class': 'form-control'}), choices= CHOISES_TAGS,
    label='Tags')

    class Meta:
        model = Question
        fields = ('header', 'body', 'tags')

class ReplyCreateForm(forms.ModelForm):
    """Форма создания ответа на вопрос. Связана с представлением ReplyCreateView."""

    class Meta:
        model = Reply
        fields = ('text',)

class RatedQuestionForm(forms.ModelForm):
    """Форма оценки вопроса. Связана с представлениями QuestionRatedUpView, QuestionRatedDownView, QuestionRatedCancelView."""

    class Meta:
        model = MTMQuestionRating
        fields = ()

class RatedReplyForm(forms.ModelForm):
    """Форма оценки ответа. Связана с представлениями ReplyRatedUpView, ReplyRatedDownView, ReplyRatedCancelView."""

    class Meta:
        model = MTMReplyRating
        fields = ()

class BestReplyForm(forms.ModelForm):
    """Форма выбора лучшего комментария. Связана с представлением BestReplySetView."""

    class Meta:
        model = MTMReplyRating
        fields = ()