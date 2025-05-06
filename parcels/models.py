from django.db import models
from django.conf import settings
from lockers.models import Locker

class Parcel(models.Model):

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_parcels', on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_parcels', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    STATUS_CHOICES = [
        ('shipment_ordered', 'Shipment ordered'),
        ('stored_in_machine', 'Stored in machine'),
        ('picked_up_by_courier', 'Picked up by courier'),
        ('delivered_to_machine', 'Delivered to machine'),
        ('received_by_recipient', 'Received by recipient'),
    ]

    size_choices = [
        ('small', 'Small'),
        ('large', 'Large'),
    ]

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='shipment_ordered')
    package_size = models.CharField(max_length=6, choices=size_choices, default='small')
    delivered_at = models.DateTimeField(null=True, blank=True)
    courier_number = models.CharField(max_length=50, blank=True, null=True)
    sent_from_machine = models.ForeignKey(Locker, related_name='sent_parcels', on_delete=models.CASCADE, null=True, blank=True)
    sent_to_machine = models.ForeignKey(Locker, related_name='received_parcels', on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Parcel {self.name} from {self.sender.username} to {self.receiver.username}"

    def is_delivered(self):
        return self.status == 'received_by_recipient'
