from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from .forms import NGO_MedicineListInfoForm, Donor_MedicineListInfoForm
from DonationSystem.models import Donor_MedicineListInfo, NGO_MedicineListInfo


# Create your views here.
@login_required
def dashboard(request):
    ngo_name = request.GET.get('ngo_name')
    if ngo_name:
        return redirect('ngo_search', ngo_name=ngo_name)
    
    if request.user.is_authenticated:
        if request.user.is_ngo:
            context = NGO_MedicineListInfo.objects.filter(NGO=request.user)
        else:
            context = Donor_MedicineListInfo.objects.filter(Donor=request.user)
        
        return render(request, 'DonationSystem/dashboard.html', {'context':context, 'is_ngo': request.user.is_ngo })

    return render(request, 'DonationSystem/dashboard.html')


@login_required
def edit_list(request):
    if request.user.is_ngo:
        context = NGO_MedicineListInfo.objects.filter(NGO=request.user)
    else:
        context = Donor_MedicineListInfo.objects.filter(Donor=request.user)
        
    return render(request, 'DonationSystem/edit_list.html', {'context':context, 'is_ngo': request.user.is_ngo })

@login_required
def add_medicine(request):
    if request.method == "POST":
        if request.user.is_ngo:
            form = NGO_MedicineListInfoForm(request.POST)
            if form.is_valid():
                MedicineName = form.cleaned_data['MedicineName']
                DosageAmount = form.cleaned_data['DosageAmount']
                MedicinePriority = form.cleaned_data['MedicinePriority']
                AmountRequired = form.cleaned_data['AmountRequired']

                NGO_MedicineListInfo.objects.create(MedicineName=MedicineName,DosageAmount=DosageAmount,MedicinePriority=MedicinePriority
                                                ,AmountRequired=AmountRequired,NGO=request.user)
                return redirect('edit-list')
                
        else:
            form = Donor_MedicineListInfoForm(request.POST,request.FILES)
            if form.is_valid():
                MedicineName = form.cleaned_data['MedicineName']
                DosageAmount = form.cleaned_data['DosageAmount']
                PillsLeft = form.cleaned_data['PillsLeft']
                ExpiryDateImage = form.cleaned_data['ExpiryDateImage']

                Donor_MedicineListInfo.objects.create(MedicineName=MedicineName,DosageAmount=DosageAmount,PillsLeft=PillsLeft
                                                ,ExpiryDateImage=ExpiryDateImage,Donor=request.user)

                
                return redirect('edit-list')

    else:
        if request.user.is_ngo:
            form = NGO_MedicineListInfoForm()
        else:
            form = Donor_MedicineListInfoForm()

    return render(request, 'DonationSystem/add_medicine.html', {'form': form, 'is_ngo': request.user.is_ngo })


@login_required
def update_medicine(request, pk):
    if request.method == "POST":
        if request.user.is_ngo:
            data= NGO_MedicineListInfo.objects.get(id=pk)
            form = NGO_MedicineListInfoForm(request.POST, instance = data)
            if form.is_valid():
                form.save()
                return redirect('edit-list')
        else:
            data= Donor_MedicineListInfo.objects.get(id=pk)
            form = Donor_MedicineListInfoForm(request.POST,request.FILES, instance = data)
            if form.is_valid():
                form.save()
                return redirect('edit-list')
    else:            
                
        if request.user.is_ngo:
            data= NGO_MedicineListInfo.objects.get(id=pk)
            form = NGO_MedicineListInfoForm(instance = data)
        else:
            data= Donor_MedicineListInfo.objects.get(id=pk)
            form = Donor_MedicineListInfoForm(instance = data)

    return render(request, 'DonationSystem/update_medicine.html', {'form': form, 'is_ngo': request.user.is_ngo })

@login_required
def delete_medicine(request, pk):
    if request.user.is_ngo:
        data = NGO_MedicineListInfo.objects.get(pk=pk).delete()
    else:
        data = Donor_MedicineListInfo.objects.get(pk=pk).delete()
    return redirect('edit-list')