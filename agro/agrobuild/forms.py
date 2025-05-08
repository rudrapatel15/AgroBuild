from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Feedback
User = get_user_model()

class RegisterForm(UserCreationForm):
    name = forms.CharField(max_length = 255, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'password1', 'password2']

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'product_name', 'category', 'review']
        widgets = {
            'review': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['product_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['category'].widget.attrs.update({'class': 'form-control'})
        self.fields['review'].widget.attrs.update({'class': 'form-control'})
