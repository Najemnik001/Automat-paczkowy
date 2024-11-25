from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    usersurname = models.CharField(max_length=150, blank=True, null=True)

    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('courier', 'Courier'),
        ('client', 'Client'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')

    def __str__(self):
        return f"{self.username} {self.usersurname}"