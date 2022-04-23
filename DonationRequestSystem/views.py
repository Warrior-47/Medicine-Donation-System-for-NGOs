from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib import messages

from .forms import donationRequestForm

# Create your views here.

def donation(request):
    if request.method == 'POST':
        form = donationRequestForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, 'Donation Request has been sent!')
            return redirect('base')
    else:
        form = donationRequestForm()
        
    return render(request, 'DonationRequestSystem/donation_request.html', {'form': form, 'title': 'donation'})

def test(request):
    return HttpResponse('<h1>test site</h1>')
        