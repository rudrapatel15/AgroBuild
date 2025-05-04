from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterForm(UserCreationForm):
    name = forms.CharField(max_length = 255, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'password1', 'password2']
