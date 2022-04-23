from django import forms


from .models import donationRequest

class donationRequestForm(forms.ModelForm):
    email = forms.EmailField(label='Email Address', required=True)

   
   
    Medicine_list = forms.CharField(label='Medicine', max_length=100, required=True)
    
    delivery_options = (
        ('In-person', 'In-person'),
        ('Pick-up', 'Pick-up'),
        
    )
    Delivery_type = forms.MultipleChoiceField(
            widget = forms.CheckboxSelectMultiple,
            choices = delivery_options
    )
    phone = forms.CharField(label='Contact Number', max_length=11, required=True)

    class Meta:
        model = donationRequest
        fields = ['email', 'Medicine_list','Delivery_type','phone']
