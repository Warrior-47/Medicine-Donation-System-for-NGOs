from django.shortcuts import redirect, render

# Create your views here.
def dashboard(request):
    ngo_name = request.GET.get('ngo_name')

    if ngo_name:
        return redirect('ngo_search', ngo_name=ngo_name)

    return render(request, 'DonationSystem/dashboard.html')