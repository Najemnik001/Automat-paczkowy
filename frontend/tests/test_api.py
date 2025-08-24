from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from parcels.models import Parcel
from lockers.models import Locker
from unittest.mock import patch
import random

User = get_user_model()

class ParcelAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        r = random.randint(1000, 9999)

        self.sender = User.objects.create_user(
            email=f'sender{r}@test.pl',
            username='Sender',
            usersurname='Kowalski',
            password='pass'
        )
        self.receiver = User.objects.create_user(
            email=f'receiver{r}@test.pl',
            username='Receiver',
            usersurname='Nowak',
            password='pass'
        )

        self.locker_from = Locker.objects.create(name='LockerA', location='Warszawa')
        self.locker_to = Locker.objects.create(name='LockerB', location='Białystok')

        self.parcel = Parcel.objects.create(
            name='Test Parcel',
            sender=self.sender,
            receiver=self.receiver,
            sent_from_machine=self.locker_from,
            sent_to_machine=self.locker_to,
            status='shipment_ordered'
        )

    # UWAGA: kolejność argumentów odpowiada kolejności patchy (najnowszy patch jest pierwszym arguemntem)
    @patch('frontend.views.send_user_notification')
    @patch('time.sleep', return_value=None)
    def test_mock_pickup_by_courier_post(self, mock_sleep, mock_notify):
        url = reverse('mock_pickup_by_courier')
        response = self.client.post(url, {'parcel_id': self.parcel.id})
        self.parcel.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.parcel.status, 'picked_up_by_courier')
        mock_notify.assert_called_once()

    def test_mock_pickup_by_courier_wrong_method(self):
        url = reverse('mock_pickup_by_courier')
        response = self.client.get(url)
        data = response.json()
        self.assertFalse(data.get('success'))

    @patch('frontend.views.send_user_notification')
    @patch('time.sleep', return_value=None)
    def test_mock_deliver_to_machine_post(self, mock_sleep, mock_notify):
        url = reverse('mock_deliver_to_machine')
        response = self.client.post(url, {'parcel_id': self.parcel.id})
        self.parcel.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.parcel.status, 'delivered_to_machine')
        mock_notify.assert_called_once()

    @patch('frontend.views.send_user_notification')
    @patch('time.sleep', return_value=None)
    def test_mock_store_parcel_post(self, mock_sleep, mock_notify):
        url = reverse('mock_store_parcel')
        response = self.client.post(url, {'parcel_id': self.parcel.id})
        self.parcel.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.parcel.status, 'stored_in_machine')
        mock_notify.assert_called_once()

    def test_mock_store_parcel_wrong_method(self):
        url = reverse('mock_store_parcel')
        response = self.client.get(url)
        data = response.json()
        self.assertFalse(data.get('success'))

    @patch('time.sleep', return_value=None)
    def test_mock_receive_parcel_post(self, mock_sleep):
        url = reverse('mock_receive_parcel')
        response = self.client.post(url, {'parcel_id': self.parcel.id})
        self.parcel.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.parcel.status, 'received_by_recipient')
        self.assertIsNotNone(self.parcel.delivered_at)
