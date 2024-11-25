from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import RegisterForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from parcels.forms import ParcelForm
from parcels.models import Parcel
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('main_page')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

@login_required
def main_page(request):
    # Pobranie paczek nadanych do użytkownika i wysłanych przez użytkownika
    received_parcels = Parcel.objects.filter(receiver=request.user)
    sent_parcels = Parcel.objects.filter(sender=request.user)

    context = {
        'received_parcels': received_parcels,
        'sent_parcels': sent_parcels,
    }

    return render(request, 'mainPage.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

def create_parcel(request):
    if request.method == 'POST':
        form = ParcelForm(request.POST)
        if form.is_valid():
            # Zapisz paczkę
            parcel = form.save(commit=False)
            parcel.sender = request.user
            parcel.save()
            messages.success(request, "Parcel has been created successfully!")
            return redirect('parcels:main')
        else:

            messages.error(request, "Error while creating parcel. Please check the details.")
    else:
        form = ParcelForm()

    return render(request, 'create_parcel.html', {'form': form})