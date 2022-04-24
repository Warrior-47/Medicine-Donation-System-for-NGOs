from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib import messages

from .forms import donationRequestForm
from  account.models import CustomUser
from DonationSystem.models import Donor_MedicineListInfo,NGO_MedicineListInfo
# Create your views here.
from DonationRequestSystem.models import donationRequest,donatedMedicines
def donation(request,pk):
    if request.method == 'POST':
        form = donationRequestForm(request.POST)
        if form.is_valid():
            donor = request.user
            ngo = CustomUser.objects.get(pk=pk)
            delivery_type = form.cleaned_data.get('Delivery_type')
            
            pickup_address=form.cleaned_data.get('Pick_up_address')
            phone =form.cleaned_data.get('phone') 

            don_req = donationRequest.objects.create(Donor=donor, NGO=ngo, Delivery_type=delivery_type, Pick_Up_address=pickup_address)
            
            donormedlist=Donor_MedicineListInfo.objects.filter(Donor=donor)
            ngomedlist=NGO_MedicineListInfo.objects.filter(NGO=ngo)
            commonmedlist=[]
            for i in donormedlist:
                for j in ngomedlist:
                    if i.MedicineName==j.MedicineName:
                        commonmedlist.append(i)
            for i in commonmedlist:
              donatedMedicines.objects.create(medicine_name=i.MedicineName,dosage_amount=i.DosageAmount, number_of_pills=i.PillsLeft,donation_request=don_req)

            messages.success(request, 'Donation Request has been sent!')
            return redirect('dashboard')
    else:
        form = donationRequestForm()
        
    return render(request, 'DonationRequestSystem/donation_request.html', {'form': form, 'title': 'donation'})

def test(request):
    return HttpResponse('<h1>test site</h1>')
        