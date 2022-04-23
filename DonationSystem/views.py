from django.shortcuts import redirect, render

from DonationSystem.models import Donor_MedicineListInfo, NGO_MedicineListInfo, Donor_MedicineListInfo
from account.models import CustomUser


# Create your views here.
def dashboard(request):
    ngo_name = request.GET.get('ngo_name')
    if ngo_name:
        return redirect('ngo_search', ngo_name=ngo_name)
    
    if request.user.is_authenticated:
        if request.user.is_ngo:
            context = NGO_MedicineListInfo.objects.filter(NGO=request.user)
        else:
            context = Donor_MedicineListInfo.objects.filter(Donor=request.user)
        
        return render(request, 'DonationSystem/dashboard.html',{'context':context, 'is_ngo': request.user.is_ngo })

    return render(request, 'DonationSystem/dashboard.html')
