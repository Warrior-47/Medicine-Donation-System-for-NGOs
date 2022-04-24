from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, HttpResponse
from django.contrib import messages

from DonationSystem.models import Donor_MedicineListInfo, NGO_MedicineListInfo
from .utilities import medicine_prioritized_data
from account.models import CustomUser

# Create your views here.
@login_required
def ngo_search(request, ngo_name):
    check = request.GET.get('ngo_name')
    if check:
        ngo_name = check

    ngo_list = CustomUser.objects.filter(fullname__icontains=ngo_name, is_ngo=True)

    if not ngo_list:
        messages.warning(request, 'No matching NGO found')
        return redirect('dashboard')

    return render(request, 'search/ngo_list.html', { 'data': ngo_list })

@login_required
def priority_search(request, search_type):
    if search_type == 'medicine':
        donor_med_list = Donor_MedicineListInfo.objects.filter(Donor=request.user)
        ngo_med_lists = NGO_MedicineListInfo.objects.values('NGO', 'MedicineName', 'MedicinePriority', 'NGO__fullname', 'NGO__email', 'NGO__phone')

        ngo_list = medicine_prioritized_data(donor_med_list, ngo_med_lists)
    elif search_type == 'distance':
        return HttpResponse("<h1>Not Implemented Yet</h1>")

    else:
        return redirect('dashboard')

    if ngo_list == []:
        messages.warning(request, 'No NGOs Found')
        return redirect('dashboard')
    return render(request, 'search/ngo_list.html', { 'data': ngo_list })

@login_required
def show_ngo_list(request, pk):
    ngo = CustomUser.objects.get(pk=pk)
    medicine_list = NGO_MedicineListInfo.objects.filter(NGO=ngo)
    return render(request, 'search/ngo_medicine_list.html', { 'medicine_list': medicine_list, 'ngo_name': ngo.fullname, 'ngo_pk': ngo.pk })