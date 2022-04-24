from django import forms


from .models import donationRequest

class donationRequestForm(forms.ModelForm):
    Medicine_list = forms.CharField(label='Medicine', max_length=100, required=True)
    
    delivery_options = (
        ('In-person', 'In-person'),
        ('Pick-up', 'Pick-up'),
        
    )
    Delivery_type = forms.ChoiceField(
           
            choices = delivery_options
    )
    Pick_up_address = forms.CharField(label='Pick-up address',max_length=100, required=False)
    phone = forms.CharField(label='Contact Number', max_length=11, required=True)

    class Meta:
        model = donationRequest
        fields = ['Medicine_list','Delivery_type','phone']
