from django.shortcuts import redirect, render
from django.contrib import messages

from account.models import CustomUser

# Create your views here.
def medicine(request):
    return render(request, 'search/ngo_list.html', { 'data': 'Medicine Priority'})

def distance(request):
    return render(request, 'search/ngo_list.html', { 'data': 'Distance Priority'})

def ngo_search(request, ngo_name):
    check = request.GET.get('ngo_name')
    if check:
        ngo_name = check

    ngo_list = CustomUser.objects.filter(fullname__icontains=ngo_name, is_ngo=True)

    if not ngo_list:
        messages.warning(request, 'No matching NGO found')
        return redirect('dashboard')

    return render(request, 'search/ngo_list.html', { 'data': ngo_list })