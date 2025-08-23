from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    usersurname = models.CharField(max_length=150, blank=False, null=True)

    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('courier', 'Courier'),
        ('client', 'Client'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')

    username = models.CharField(
        max_length=150,
        unique=False,
        verbose_name="Imię"
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Adres e-mail"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'usersurname']

    def __str__(self):
        return f"{self.username} {self.usersurname}"
