from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render, HttpResponse

from common.decorators import login_required
from common.service_client import ServiceUnavailable, internal_get
from .utilities import medicine_prioritized_data

# Create your views here.
@login_required
def ngo_search(request, ngo_name):
    check = request.GET.get('ngo_name')
    if check:
        ngo_name = check

    try:
        payload = internal_get(settings.USER_SERVICE_URL, '/api/ngos/', params={'name': ngo_name})
    except ServiceUnavailable:
        messages.error(request, 'Search is temporarily unavailable, please try again')
        return redirect('/')

    ngo_list = [dict(ngo, pk=ngo['id']) for ngo in payload['ngos']]

    if not ngo_list:
        messages.warning(request, 'No matching NGO found')
        return redirect('/')

    return render(request, 'search/ngo_list.html', { 'data': ngo_list })

@login_required
def priority_search(request, search_type):
    if search_type == 'medicine':
        try:
            donor_meds = internal_get(
                settings.MEDICINE_SERVICE_URL, f'/api/medicines/donor/{request.user.id}/'
            )['medicines']
            ngo_meds = internal_get(settings.MEDICINE_SERVICE_URL, '/api/medicines/ngo/')['medicines']

            def fetch_users(ids):
                params = {'ids': ','.join(str(i) for i in ids)}
                return internal_get(settings.USER_SERVICE_URL, '/api/users/', params=params)['users']

            ngo_list = medicine_prioritized_data(donor_meds, ngo_meds, fetch_users)
        except ServiceUnavailable:
            messages.error(request, 'Search is temporarily unavailable, please try again')
            return redirect('/')
    elif search_type == 'distance':
        return HttpResponse("<h1>Not Implemented Yet</h1>")

    else:
        return redirect('/')

    if ngo_list == []:
        messages.warning(request, 'No NGOs Found')
        return redirect('/')
    return render(request, 'search/ngo_list.html', { 'data': ngo_list })

@login_required
def show_ngo_list(request, pk):
    try:
        ngo = internal_get(settings.USER_SERVICE_URL, f'/api/users/{pk}/')
        medicines = internal_get(settings.MEDICINE_SERVICE_URL, f'/api/medicines/ngo/{pk}/')['medicines']
    except ServiceUnavailable:
        messages.error(request, 'Search is temporarily unavailable, please try again')
        return redirect('/')

    if ngo is None:
        messages.warning(request, 'No matching NGO found')
        return redirect('/')

    return render(request, 'search/ngo_medicine_list.html', { 'medicine_list': medicines, 'ngo_name': ngo['fullname'], 'ngo_pk': ngo['id'] })
