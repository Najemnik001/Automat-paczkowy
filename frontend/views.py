from django.conf import settings
from users.forms import RegisterForm
from users.forms import CustomAuthenticationForm
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from parcels.forms import ParcelForm
from parcels.models import Parcel
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from lockers.models import Lock
from users.models import CustomUser
from django.db.models import Q
from lockers.forms import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import time
from webpush import send_user_notification
from django.views.decorators.http import require_POST
from parcels.models import ParcelCourierHistory, CourierAction

User = settings.AUTH_USER_MODEL


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Rejestracja zakończona sukcesem! Możesz teraz się zalogować.")
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            user = form.get_user()
            if user.role == 'admin':
                return redirect('admin_panel')
            elif user.role == 'courier':
                return redirect('courier_view')
            return redirect('main_page')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def main_page(request):
    received_parcels = Parcel.objects.filter(receiver=request.user)
    sent_parcels = Parcel.objects.filter(sender=request.user)

    context = {
        'received_parcels': received_parcels,
        'sent_parcels': sent_parcels,
        'vapid_key': settings.WEBPUSH_SETTINGS["VAPID_PUBLIC_KEY"]
    }

    return render(request, 'mainPage.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

def is_client(user):
    return user.is_authenticated and user.role == 'client'

@user_passes_test(is_client)
def create_parcel(request):
    lockers = Locker.objects.all()

    if request.method == 'POST':
        form = ParcelForm(request.POST)
        if form.is_valid():
            receiver = form.cleaned_data['receiver_email']

            if receiver == request.user:
                messages.error(request, "Nie możesz wysłać paczki do samego siebie.")
                return render(request, 'create_parcel.html', {'form': form, 'lockers': lockers})

            parcel = form.save(commit=False)
            parcel.sender = request.user
            parcel.receiver = receiver
            parcel.delivery_status = 'Shipment ordered'
            parcel.sent_from_machine = form.cleaned_data['sent_from_machine']
            parcel.sent_to_machine = form.cleaned_data['sent_to_machine']
            parcel.save()
            return redirect('main_page')
        else:
            messages.error(request, "Nie udało się utworzyć paczki. Sprawdź poprawność danych.")

    else:
        search_query = request.GET.get('search', '')
        if search_query:
            lockers = lockers.filter(name__icontains=search_query) | lockers.filter(location__icontains=search_query)
        form = ParcelForm()

    return render(request, 'create_parcel.html', {'form': form, 'lockers': lockers})




def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

def is_courier(user):
    return user.is_authenticated and user.role == 'courier'




@user_passes_test(is_admin)
def admin_panel(request):
    search_lockers = (request.GET.get('search_lockers') or '').strip()
    search_users   = (request.GET.get('search_users') or '').strip()

    lockers = Locker.objects.filter(
        Q(name__icontains=search_lockers) | Q(location__icontains=search_lockers)
    ) if search_lockers else Locker.objects.none()

    users = CustomUser.objects.filter(
        Q(email__icontains=search_users) |
        Q(username__icontains=search_users) |
        Q(usersurname__icontains=search_users)
    ) if search_users else CustomUser.objects.none()

    context = {
        'lockers': lockers,
        'users': users,
        'search_lockers': search_lockers,
        'search_users': search_users,
    }
    return render(request, 'admin_panel.html', context)


@user_passes_test(is_admin)
def add_locker(request):
    if request.method == 'POST':
        form = LockerForm(request.POST)
        if form.is_valid():

            locker = form.save()
            small_boxes = form.cleaned_data['small_boxes']
            large_boxes = form.cleaned_data['large_boxes']

            for _ in range(small_boxes):
                Lock.objects.create(locker=locker, size='small', is_free=True)

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

            new_small_boxes = form.cleaned_data['small_boxes']
            new_large_boxes = form.cleaned_data['large_boxes']

            current_small_boxes = locker.locks.filter(size='small').count()
            current_large_boxes = locker.locks.filter(size='large').count()

            if new_small_boxes < current_small_boxes:

                free_locks = locker.locks.filter(size='small', is_free=True)
                locks_to_delete_count = current_small_boxes - new_small_boxes

                if free_locks.count() < locks_to_delete_count:
                    messages.error(request, "Nie można zmniejszyć liczby skrytek: niektóre są zajęte.")
                    return render(request, 'edit_locker.html', {'form': form, 'locker': locker})


                for lock in free_locks[:locks_to_delete_count]:
                    lock.delete()

            elif new_small_boxes > current_small_boxes:

                for _ in range(new_small_boxes - current_small_boxes):
                    Lock.objects.create(locker=locker, size='small', is_free=True)

            if new_large_boxes < current_large_boxes:

                free_locks = locker.locks.filter(size='large', is_free=True)
                locks_to_delete_count = current_large_boxes - new_large_boxes

                if free_locks.count() < locks_to_delete_count:
                    messages.error(request, "Nie można zmniejszyć liczby skrytek: niektóre są zajęte.")
                    return render(request, 'edit_locker.html', {'form': form, 'locker': locker})

                for lock in free_locks[:locks_to_delete_count]:
                    lock.delete()

            elif new_large_boxes > current_large_boxes:
                for _ in range(new_large_boxes - current_large_boxes):
                    Lock.objects.create(locker=locker, size='large', is_free=True)

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
    return redirect('user_report')


@user_passes_test(is_admin)
def user_report(request):
    users = CustomUser.objects.all().order_by('id')
    return render(request, 'raport_users.html', {'users': users})

@user_passes_test(is_admin)
def change_user_role(request, user_id):
    if request.method != 'POST':
        messages.error(request, "Nieprawidłowa metoda.")
        return redirect('user_report')

    user = get_object_or_404(CustomUser, id=user_id)
    new_role = request.POST.get('role')

    if new_role not in ['admin', 'courier', 'client']:
        messages.error(request, "Nieprawidłowa rola.")
        return redirect('user_report')

    user.role = new_role
    user.save()
    messages.success(request, f"Zmieniono rolę użytkownika {user.username} na: {new_role}.")
    return redirect('user_report')

@user_passes_test(is_admin)
@require_POST
def update_user_role(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    new_role = request.POST.get('role')
    if new_role not in ('admin', 'courier', 'client'):
        return JsonResponse({'success': False, 'message': 'Nieprawidłowa rola.'}, status=400)
    user.role = new_role
    user.save()
    return JsonResponse({'success': True})

@user_passes_test(is_admin)
def parcel_report(request):
    q = (request.GET.get('q') or '').strip()

    parcels = Parcel.objects.all()

    if q:
        parcels = parcels.filter(
            Q(sender__email__icontains=q) |
            Q(receiver__email__icontains=q) |
            Q(courier_number__email__icontains=q) |
            Q(sent_from_machine__name__icontains=q) |
            Q(sent_from_machine__location__icontains=q) |
            Q(sent_to_machine__name__icontains=q) |
            Q(sent_to_machine__location__icontains=q)
        )


    context = {
        'parcels': parcels.select_related(
        'sender', 'receiver', 'courier_number', 'sent_from_machine', 'sent_to_machine'
    ).prefetch_related(
        'courier_history__courier'
    ),
        'q': q,
    }
    return render(request, 'raport_parcels.html', context)

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
            parcel.courier_number = request.user
            parcel.save()
            messages.success(request, f"Zmieniono status paczki {parcel.name} na {parcel.get_status_display()}.")

        return redirect('courier_view')

    lockers_with_parcels = []
    for locker in lockers:
        to_pick_up = locker.sent_parcels.filter(status='stored_in_machine')
        to_deliver = locker.received_parcels.filter(status='picked_up_by_courier')

        if to_pick_up.exists() or to_deliver.exists():
            lockers_with_parcels.append({
                'locker': locker,
                'to_pick_up': to_pick_up,
                'to_deliver': to_deliver,
            })

    context['lockers_with_parcels'] = lockers_with_parcels
    return render(request, 'courier_view.html', context)


@csrf_exempt
def mock_pickup_by_courier(request):
    if request.method == "POST":
        parcel_id = request.POST.get("parcel_id")
        try:
            parcel = Parcel.objects.get(id=parcel_id)

            time.sleep(5)

            parcel.status = "picked_up_by_courier"
            parcel.courier_number = request.user
            parcel.save()

            parcel.log_courier_action(request.user, CourierAction.PICKUP)

            payload = {
                "head": "Paczka w drodze!",
                "body": f"Kurier odebrał twoją paczkę: '{parcel.name}'.",
                "url": "https://najemnik001.pythonanywhere.com/main_page/"
            }

            try:
                send_user_notification(user=parcel.sender, payload=payload, ttl=1000)
            except Exception as e:
                print(f"Błąd przy wysyłaniu powiadomienia: {e}")

            return JsonResponse({'success': True})

        except Parcel.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Paczka nie istnieje'})

    return JsonResponse({'success': False, 'message': 'Błędna metoda HTTP'})


@csrf_exempt
def mock_deliver_to_machine(request):
    if request.method == "POST":
        parcel_id = request.POST.get("parcel_id")
        try:
            parcel = Parcel.objects.get(id=parcel_id)

            time.sleep(5)

            parcel.status = "delivered_to_machine"
            parcel.courier_number = request.user
            parcel.save()

            parcel.log_courier_action(request.user, CourierAction.DROPOFF)

            payload = {
                "head": "Twoja paczka dotarła!",
                "body": f"Paczka '{parcel.name}' czeka na odbiór w automacie: {parcel.sent_to_machine.name}",
                "url": "https://najemnik001.pythonanywhere.com/main_page/"
            }

            try:
                send_user_notification(user=parcel.receiver, payload=payload, ttl=1000)
            except Exception as e:
                print(f"Błąd przy wysyłaniu powiadomienia: {e}")

            return JsonResponse({'success': True})

        except Parcel.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Paczka nie istnieje'})

    return JsonResponse({'success': False, 'message': 'Błędna metoda HTTP'})

@csrf_exempt
def mock_store_parcel(request):
    if request.method == "POST":
        parcel_id = request.POST.get('parcel_id')
        try:
            parcel = Parcel.objects.get(id=parcel_id)
            time.sleep(5)
            parcel.status = 'stored_in_machine'
            parcel.save()

            if parcel.receiver:
                payload = {
                    "head": "Twoja paczka jest już w automacie!",
                    "body": f"Paczka '{parcel.name}' od {parcel.sender.username} została umieszczona w automacie.",
                    "url": "https://najemnik001.pythonanywhere.com/main_page/"
                }
                send_user_notification(user=parcel.receiver, payload=payload, ttl=1000)

            return JsonResponse({'success': True})
        except Parcel.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Paczka nie została znaleziona.'})
    return JsonResponse({'success': False, 'message': 'Nieprawidłowa metoda zapytania.'})

@csrf_exempt
def mock_receive_parcel(request):
    if request.method == 'POST':
        parcel_id = request.POST.get('parcel_id')
        try:
            parcel = Parcel.objects.get(id=parcel_id)
            time.sleep(5)
            parcel.status = 'received_by_recipient'
            parcel.delivered_at = timezone.now()
            parcel.save()
            return JsonResponse({'success': True})
        except Parcel.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Paczka nie istnieje'})
    return JsonResponse({'success': False, 'message': 'Błędna metoda HTTP'})


