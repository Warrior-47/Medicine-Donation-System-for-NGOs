from django.shortcuts import render
from django.contrib import messages


from .forms import RegistrationForm

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')

    else:
        form = RegistrationForm()
        
    return render(request, 'account/register.html', {'form': form, 'title': 'Register'})