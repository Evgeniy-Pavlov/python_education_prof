from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import UserBase, Question, Tags, Reply

class RegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Login')
    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Email')
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Repeat password')
    logo = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control', 'style': 'width: 500px;'}), required=False, label='Avatar')

    class Meta:
        model = UserBase
        fields = ('username', 'email', 'password1', 'password2', 'logo')