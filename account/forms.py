from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(label='Email Address', required=True)

    is_ngo = forms.BooleanField(label="Create An NGO Account", required=False)

    fullname = forms.CharField(label='Full Name', max_length=100, required=True)
    identity = forms.CharField(label='Identity', max_length=10, required=True)
    phone = forms.CharField(label='Contact Number', max_length=11, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'is_ngo', 'fullname', 'identity', 'phone']
