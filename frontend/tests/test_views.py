from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from parcels.models import Parcel
from lockers.models import Locker
import random

User = get_user_model()

class SimpleViewsTests(TestCase):

    def setUp(self):
        self.client = Client()
        r = random.randint(1000, 9999)

        self.user = User.objects.create_user(
            email=f'testuser{r}@example.com',
            username='Testuser',
            usersurname='Kowalski',
            password='password',
            role='client'
        )
        self.admin = User.objects.create_user(
            email=f'admin{r}@example.com',
            username='Admin',
            usersurname='Adminowski',
            password='password',
            role='admin'
        )
        self.courier = User.objects.create_user(
            email=f'courier{r}@example.com',
            username='Courier',
            usersurname='Kurierowski',
            password='password',
            role='courier'
        )

        self.locker = Locker.objects.create(name='LockerA', location='Warszawa')

        self.parcel = Parcel.objects.create(
            name='TestParcel',
            sender=self.user,
            receiver=self.admin,
            sent_from_machine=self.locker,
            sent_to_machine=self.locker
        )

    def test_main_page_renders(self):
        self.client.login(username=self.user.email, password='password')
        response = self.client.get(reverse('main_page'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('received_parcels', response.context)

    def test_create_parcel_get(self):
        self.client.login(username=self.user.email, password='password')
        response = self.client.get(reverse('create_parcel'))
        self.assertEqual(response.status_code, 200)

    def test_courier_view_get(self):
        self.client.login(username=self.courier.email, password='password')
        response = self.client.get(reverse('courier_view'))
        self.assertEqual(response.status_code, 200)

    def test_user_report_renders(self):
        self.client.login(username=self.admin.email, password='password')
        response = self.client.get(reverse('user_report'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('users', response.context)

    def test_parcel_report_renders(self):
        self.client.login(username=self.admin.email, password='password')
        response = self.client.get(reverse('parcel_report'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('parcels', response.context)
