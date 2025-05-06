from django.conf import settings
from users.forms import RegisterForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from parcels.forms import ParcelForm
from parcels.models import Parcel
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from lockers.models import Locker, Lock
from users.models import CustomUser
from django.db.models import Q
from lockers.forms import *


User = settings.AUTH_USER_MODEL


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            login(request, user)

            messages.success(request, "Rejestracja zakończona sukcesem! Możesz teraz się zalogować.")
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
                # Sprawdź rolę użytkownika i przekieruj na odpowiednią stronę
                if user.role == 'admin':
                    return redirect('admin_panel')  # Przekierowanie na panel admina
                elif user.role == 'courier':
                    return redirect('courier_view') # Przekierowanie na panel kuriera
                else:
                    return redirect('main_page')  # Przekierowanie na główną stronę dla zwykłych użytkowników
            else:
                messages.error(request, "Nieprawidłowe dane logowania.")
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

from django.contrib.auth import get_user_model

def create_parcel(request):
    lockers = Locker.objects.all()

    # Obsługa POST – tworzenie paczki
    if request.method == 'POST':
        form = ParcelForm(request.POST)
        if form.is_valid():
            receiver = form.cleaned_data['receiver_email']

            # Nie pozwalamy wysłać paczki do siebie samego
            if receiver == request.user:
                messages.error(request, "Nie możesz wysłać paczki do samego siebie.")
                return render(request, 'create_parcel.html', {'form': form, 'lockers': lockers})

            parcel = form.save(commit=False)
            parcel.sender = request.user
            parcel.receiver = receiver
            parcel.delivery_status = 'Shipment ordered'
            parcel.sent_from_locker = form.cleaned_data['sent_from_locker']
            parcel.sent_to_locker = form.cleaned_data['sent_to_locker']
            parcel.save()

            messages.success(request, "Przesyłka została utworzona pomyślnie.")
            return redirect('main_page')
        else:
            messages.error(request, "Użytkownik o podanym adresie email nie istnieje")

    # Obsługa GET – wyświetlenie formularza
    else:
        search_query = request.GET.get('search', '')
        if search_query:
            lockers = lockers.filter(name__icontains=search_query) | lockers.filter(location__icontains=search_query)
        form = ParcelForm()

    return render(request, 'create_parcel.html', {'form': form, 'lockers': lockers})



def is_admin(user):
    return user.is_authenticated and user.role == 'admin'



# Panel administratora
@user_passes_test(is_admin)
def admin_panel(request):
    if request.method == 'POST':
        # Jeśli użytkownik wprowadził zapytanie do wyszukiwania
        search_lockers = request.POST.get('search_lockers')
        search_users = request.POST.get('search_users')

        lockers = Locker.objects.filter(
            Q(name__icontains=search_lockers) | Q(location__icontains=search_lockers)
        ) if search_lockers else Locker.objects.none()

        users = CustomUser.objects.filter(
            Q(email__icontains=search_users) |
            Q(username__icontains=search_users) |
            Q(usersurname__icontains=search_users)
        ) if search_users else CustomUser.objects.none()

        return render(request, 'admin_panel.html', {'lockers': lockers, 'users': users})

    return render(request, 'admin_panel.html')


@user_passes_test(is_admin)
def add_locker(request):
    if request.method == 'POST':
        form = LockerForm(request.POST)
        if form.is_valid():
            # Zapisujemy obiekt Locker
            locker = form.save()

            # Pobieramy liczby skrytek z formularza
            small_boxes = form.cleaned_data['small_boxes']
            large_boxes = form.cleaned_data['large_boxes']

            # Tworzymy skrytki o rozmiarze small
            for _ in range(small_boxes):
                Lock.objects.create(locker=locker, size='small', is_free=True)

            # Tworzymy skrytki o rozmiarze large
            for _ in range(large_boxes):
                Lock.objects.create(locker=locker, size='large', is_free=True)

            return redirect('admin_panel')
    else:
        form = LockerForm()

    return render(request, 'add_locker.html', {'form': form})


@user_passes_test(is_admin)
def edit_locker(request, locker_id):
    locker = get_object_or_404(Locker, id=locker_id)

    if request.method == 'POST':
        form = LockerEditForm(request.POST, locker=locker)
        if form.is_valid():
            # Pobieramy nową liczbę skrytek
            new_small_boxes = form.cleaned_data['small_boxes']
            new_large_boxes = form.cleaned_data['large_boxes']

            # Pobieramy aktualną liczbę skrytek
            current_small_boxes = locker.locks.filter(size='small').count()
            current_large_boxes = locker.locks.filter(size='large').count()

            # Obsługa zmian dla small boxes
            if new_small_boxes < current_small_boxes:
                # Znajdujemy wolne skrytki do usunięcia
                free_locks = locker.locks.filter(size='small', is_free=True)
                locks_to_delete_count = current_small_boxes - new_small_boxes

                if free_locks.count() < locks_to_delete_count:
                    messages.error(request, "Nie można zmniejszyć liczby skrytek: niektóre są zajęte.")
                    return render(request, 'edit_locker.html', {'form': form, 'locker': locker})

                # Usuwamy wolne skrytki
                for lock in free_locks[:locks_to_delete_count]:
                    lock.delete()  # Prawidłowe usuwanie

            elif new_small_boxes > current_small_boxes:
                # Dodajemy brakujące skrytki
                for _ in range(new_small_boxes - current_small_boxes):
                    Lock.objects.create(locker=locker, size='small', is_free=True)

            # Obsługa zmian dla large boxes
            if new_large_boxes < current_large_boxes:
                # Znajdujemy wolne skrytki do usunięcia
                free_locks = locker.locks.filter(size='large', is_free=True)
                locks_to_delete_count = current_large_boxes - new_large_boxes

                if free_locks.count() < locks_to_delete_count:
                    messages.error(request, "Nie można zmniejszyć liczby skrytek: niektóre są zajęte.")
                    return render(request, 'edit_locker.html', {'form': form, 'locker': locker})

                # Usuwamy wolne skrytki
                for lock in free_locks[:locks_to_delete_count]:
                    lock.delete()  # Prawidłowe usuwanie

            elif new_large_boxes > current_large_boxes:
                # Dodajemy brakujące skrytki
                for _ in range(new_large_boxes - current_large_boxes):
                    Lock.objects.create(locker=locker, size='large', is_free=True)

            # Aktualizujemy dane Locker (np. nazwę i lokalizację)
            locker.name = form.cleaned_data['name']
            locker.location = form.cleaned_data['location']
            locker.save()

            messages.success(request, "Skrytka została zaktualizowana.")
            return redirect('admin_panel')
    else:
        form = LockerEditForm(locker=locker)

    return render(request, 'edit_locker.html', {'form': form, 'locker': locker})



@user_passes_test(is_admin)
def delete_locker(request, locker_id):
    locker = get_object_or_404(Locker, id=locker_id)
    locker.delete()
    return redirect('admin_panel')


@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    return redirect('admin_panel')

def is_courier(user):
    return user.is_authenticated and user.role == 'courier'

@user_passes_test(is_courier)
def courier_view(request):
    lockers = Locker.objects.all()
    context = {}

    if request.method == 'POST':
        parcel_id = request.POST.get('parcel_id')
        new_status = request.POST.get('new_status')

        parcel = get_object_or_404(Parcel, id=parcel_id)

        if new_status in ['picked_up_by_courier', 'delivered_to_machine']:
            parcel.status = new_status
            parcel.save()
            messages.success(request, f"Zmieniono status paczki {parcel.name} na {parcel.get_status_display()}.")

        return redirect('courier_view')

    # Przygotowanie listy paczek dla każdego automatu
    lockers_with_parcels = []
    for locker in lockers:
        to_pick_up = locker.sent_parcels.filter(status='stored_in_machine')  # paczki do odbioru z automatu
        to_deliver = locker.received_parcels.filter(status='picked_up_by_courier')  # paczki do dostarczenia do automatu

        if to_pick_up.exists() or to_deliver.exists():
            lockers_with_parcels.append({
                'locker': locker,
                'to_pick_up': to_pick_up,
                'to_deliver': to_deliver,
            })

    context['lockers_with_parcels'] = lockers_with_parcels
    return render(request, 'courier_view.html', context)


