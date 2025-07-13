from dataclasses import field
from django.forms import ModelForm

from django import forms

from account.models import CustomUser
from .models import NGO_MedicineListInfo, Donor_MedicineListInfo

class NGO_MedicineListInfoForm(ModelForm):
    MedicineName = forms.CharField(label='Medicine Name', max_length=100, required=True)
    DosageAmount = forms.IntegerField(label='Dosage Amount',required=True)
    MedicinePriority = forms.IntegerField(label='Medicine Priority', required=True)
    AmountRequired = forms.IntegerField(label='Amount Required', required=True)

    class Meta:
        model = NGO_MedicineListInfo
        fields = ('MedicineName', 'DosageAmount', 'MedicinePriority', 'AmountRequired')

class Donor_MedicineListInfoForm(ModelForm):
    class Meta:
        model = Donor_MedicineListInfo
        fields = ('MedicineName', 'DosageAmount', 'PillsLeft', 'ExpiryDateImage')
        labels = {
        'MedicineName': 'Medicine Name',
        'DosageAmount' : 'Dosage Amount',
        'PillsLeft' : 'Pills Left',
        'ExpiryDateImage' : 'Expiry Date Image',
    }


