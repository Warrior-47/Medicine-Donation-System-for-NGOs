from django import forms

from .models import CustomUser

class RegistrationForm(forms.ModelForm):
    username = forms.CharField(label='Username', max_length=100, required=True)
    email = forms.EmailField(label='Email', required=True)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    is_ngo = forms.BooleanField(label="Create An NGO Account", required=False)

    fullname = forms.CharField(label='Full Name', max_length=100, required=True)
    identity = forms.CharField(label='Identity', max_length=10, required=True)
    phone = forms.CharField(label='Contact Number', max_length=11, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'is_ngo', 'fullname', 'identity', 'phone']
