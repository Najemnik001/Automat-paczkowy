from django.test import TestCase
from django.contrib.auth import get_user_model
from lockers.models import Locker
from parcels.models import Parcel
import random

User = get_user_model()

class ParcelModelTest(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username="Jan",
            usersurname="Kowalski",
            email=f"sender{random.randint(1000, 9999)}@example.com",
            password="Test12345",
            role="client",
        )
        self.receiver = User.objects.create_user(
            username="Anna",
            usersurname="Nowak",
            email=f"receiver{random.randint(1000, 9999)}@example.com",
            password="Test12345",
            role="client",
        )
        self.courier = User.objects.create_user(
            username="Kurier",
            usersurname="Abacki",
            email=f"courier{random.randint(1000, 9999)}@example.com",
            password="Test12345",
            role="courier",
        )

        self.locker_from = Locker.objects.create(name="LockerA", location="Warszawa")
        self.locker_to = Locker.objects.create(name="LockerB", location="Białystok")

        self.parcel = Parcel.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            name="Test Parcel",
            package_size="small",
            courier_number=self.courier,
            sent_from_machine=self.locker_from,
            sent_to_machine=self.locker_to,
        )

    def test_str_method(self):
        self.assertEqual(
            str(self.parcel),
            f"Paczka {self.parcel.name} od {self.sender.username} do {self.receiver.username}",
        )

    def test_default_status(self):
        self.assertEqual(self.parcel.status, "shipment_ordered")

    def test_is_delivered_false(self):
        self.assertFalse(self.parcel.is_delivered())

    def test_is_delivered_true(self):
        self.parcel.status = "received_by_recipient"
        self.parcel.save()
        self.assertTrue(self.parcel.is_delivered())
