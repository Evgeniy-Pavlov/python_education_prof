from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
from .models import UserBase, Question, Tags, Reply
from .widgets import ModifiedClearableFileInput

class RegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Login', max_length=40)
    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Email')
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Repeat password')
    logo = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control', 'style': 'width: 500px;'}), required=False, label='Avatar')

    class Meta:
        model = UserBase
        fields = ('username', 'email', 'password1', 'password2', 'logo')
    
class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Login')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Password')

    class Meta:
        model = UserBase
        fields = ('username', 'password')

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Email')
    logo = forms.ImageField(widget=ModifiedClearableFileInput(attrs={'class': 'form-control', 'style': 'width: 500px;'}), required=False, label='Avatar')
    
    class Meta:
        model = UserBase
        fields = ('email', 'logo')

class QuestionCreateForm(forms.ModelForm):
    header = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Title', max_length=200)
    body = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), label='Text', max_length=2000)

    class Meta:
        model = Question
        fields = ('header', 'body')

class ReplyCreateForm(forms.ModelForm):

    class Meta:
        model = Reply
        fields = ('text',)
