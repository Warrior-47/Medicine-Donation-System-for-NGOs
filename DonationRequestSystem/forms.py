from django import forms
from django.forms.widgets import NumberInput

from .models import donationRequest

class donationRequestForm(forms.ModelForm):
    delivery_options = (
        ('In-person', 'In-person'),
        ('Pick-up', 'Pick-up'),
    )
    
    Delivery_type = forms.ChoiceField(
            choices = delivery_options
    )
    
    Pick_up_address = forms.CharField(label='Pick-up address',widget=forms.TextInput(attrs={'placeholder': 'provide address if you chose pick-up'}),max_length=100, required=False)

    class Meta:
        model = donationRequest
        fields = ('Delivery_type',)

class deliveryDetails(forms.ModelForm):
    pickupDate = forms.DateField(label='Pick-up Date',widget=NumberInput(attrs={'type': 'date'}),required=True)
    pickupTime = forms.TimeField(label='Pick-up Time',widget=NumberInput(attrs={'type': 'time'}),required=True)

    class Meta:
        model = donationRequest
        fields = ['pickupDate','pickupTime']