from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib import messages

from common.decorators import login_required

from .forms import donationRequestForm,deliveryDetails
from DonationRequestSystem.models import donationRequest,donatedMedicines
from common.service_client import ServiceUnavailable, internal_get

# Donation form for donor
@login_required
def donation(request,pk):
    if request.method == 'POST':
        form = donationRequestForm(request.POST)
        if form.is_valid():
            donor = request.user
            delivery_type = form.cleaned_data.get('Delivery_type')

            pickup_address=form.cleaned_data.get('Pick_up_address')

            try:
                ngo = internal_get(settings.USER_SERVICE_URL, f'/api/users/{pk}/')
                donormedlist = internal_get(
                    settings.MEDICINE_SERVICE_URL, f'/api/medicines/donor/{donor.id}/'
                )['medicines']
                ngomedlist = internal_get(
                    settings.MEDICINE_SERVICE_URL, f'/api/medicines/ngo/{pk}/'
                )['medicines']
            except ServiceUnavailable:
                messages.error(request, 'Donations are temporarily unavailable, please try again')
                return redirect('/')

            if ngo is None:
                messages.warning(request, 'No matching NGO found')
                return redirect('/')

            don_req = donationRequest.objects.create(
                Donor_id=donor.id, Donor_name=donor.fullname, Donor_phone=donor.phone,
                NGO_id=ngo['id'], NGO_name=ngo['fullname'],
                Delivery_type=delivery_type, Pick_Up_address=pickup_address)

            commonmedlist=[]
            for i in donormedlist:
                for j in ngomedlist:
                    if i['MedicineName']==j['MedicineName']:
                        commonmedlist.append(i)
            for i in commonmedlist:
                donatedMedicines.objects.create(medicine_name=i['MedicineName'],dosage_amount=i['DosageAmount'], number_of_pills=i['PillsLeft'],donation_request=don_req)

            messages.success(request, 'Donation Request has been sent!')
            return redirect('/')
    else:
        form = donationRequestForm()

    return render(request, 'DonationRequestSystem/donation_request.html', {'form': form, 'title': 'donation'})

# Notification Page
@login_required
def donation_decision(request):
    if request.user.is_authenticated:
        if request.user.is_ngo:
            req_data = donationRequest.objects.filter(NGO_id=request.user.id,Acceptance_Status=False)
            context = []
            for i in req_data:
                if len(donatedMedicines.objects.filter(donation_request=i)) != 0:
                    context.append(i)

            accepted_donors = donationRequest.objects.filter(NGO_id=request.user.id,Acceptance_Status=True,Delivery_status='pending')
            return render(request,  'DonationRequestSystem/ngo_notification.html',{ 'context':context, 'is_ngo': request.user.is_ngo, 'accepted_donors':accepted_donors })

        else:
            req_data = donationRequest.objects.filter(Donor_id=request.user.id)
            context = list(req_data.filter(Acceptance_Status=True))

            for i in req_data.filter(Acceptance_Status=False):
                if len(donatedMedicines.objects.filter(donation_request=i)) == 0:
                    context.append(i)

            return render(request,  'DonationRequestSystem/ngo_notification.html',{ 'context':context, 'is_ngo': request.user.is_ngo })

    return render(request, 'DonationRequestSystem/ngo_notification.html')

# Choose Pickup Date and Time for NGO
@login_required
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
@login_required
def donationDetailsInPerson(request,pk):

    request_obj = donationRequest.objects.get(pk=pk)

    donationRequest.objects.filter(pk=pk).update(Acceptance_Status=True)

    return redirect('ngo_notification')

# NGO Rejecting Request
@login_required
def donationReject(request, pk):
    donatedMedicines.objects.filter(donation_request=pk).delete()
    return redirect('/')

@login_required
def donationComplete(request,pk):
    donationRequest.objects.filter(pk=pk).update(Delivery_status='Complete')
    return redirect('ngo_notification')
