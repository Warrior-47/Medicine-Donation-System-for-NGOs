from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib import messages

from DonationSystem.views import dashboard

from .forms import donationRequestForm,deliveryDetails
from  account.models import CustomUser
from DonationSystem.models import Donor_MedicineListInfo,NGO_MedicineListInfo
from DonationRequestSystem.models import donationRequest,donatedMedicines

# Donation form for donor
def donation(request,pk):
    if request.method == 'POST':
        form = donationRequestForm(request.POST)
        if form.is_valid():
            donor = request.user
            ngo = CustomUser.objects.get(pk=pk)
            delivery_type = form.cleaned_data.get('Delivery_type')
            
            pickup_address=form.cleaned_data.get('Pick_up_address')

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

# Notification Page
def donation_decision(request):
    if request.user.is_authenticated:
        if request.user.is_ngo:
            req_data = donationRequest.objects.filter(NGO=request.user,Acceptance_Status=False)
            context = []
            for i in req_data:
                if len(donatedMedicines.objects.filter(donation_request=i)) != 0:
                    context.append(i)

            accepted_donors = donationRequest.objects.filter(NGO=request.user,Acceptance_Status=True,Delivery_status='pending')
            return render(request,  'DonationRequestSystem/ngo_notification.html',{ 'context':context, 'is_ngo': request.user.is_ngo, 'accepted_donors':accepted_donors })

        else:
            req_data = donationRequest.objects.filter(Donor=request.user)
            context = list(req_data.filter(Acceptance_Status=True))
            
            for i in req_data.filter(Acceptance_Status=False):
                if len(donatedMedicines.objects.filter(donation_request=i)) == 0:
                    context.append(i)

            return render(request,  'DonationRequestSystem/ngo_notification.html',{ 'context':context, 'is_ngo': request.user.is_ngo })
    
    return render(request, 'DonationRequestSystem/ngo_notification.html')

# Choose Pickup Date and Time for NGO
def donationDetails(request,pk):
    request_obj = donationRequest.objects.get(pk=pk)
    form = deliveryDetails(instance=request_obj)

    if request.method == 'POST':
        form = deliveryDetails(request.POST)
        if form.is_valid():
            date = form.cleaned_data.get('pickupDate')
            time = form.cleaned_data.get('pickupTime')
            donationRequest.objects.filter(pk=pk).update(Pick_Up_date=date, Pick_Up_time=time,Acceptance_Status=True)
            
            return redirect('ngo_notification')

    return render(request, 'DonationRequestSystem/donation_details.html',{'form': form, 'title': 'donation'})        

# NGO Accepting In-Person Request
def donationDetailsInPerson(request,pk):
    
    request_obj = donationRequest.objects.get(pk=pk)
    
    donationRequest.objects.filter(pk=pk).update(Acceptance_Status=True)

    return redirect('ngo_notification')

# NGO Rejecting Request
def donationReject(request, pk):
    donatedMedicines.objects.filter(donation_request=pk).delete()
    return redirect('dashboard')

def donationComplete(request,pk):
    donationRequest.objects.filter(pk=pk).update(Delivery_status='Complete')
    return redirect('ngo_notification')